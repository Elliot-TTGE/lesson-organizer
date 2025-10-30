<script lang="ts">
  import type { Lesson, Student, UserLesson, User } from "../../types/index.d";
  import { deleteLesson, updateLesson, createLesson, fetchLesson } from "../../api/lesson";
  import { addLessonToState, lessonState, removeLessonFromState, updateLessonInState } from "$lib/states/lessonState.svelte";
  import type { LessonCreateFields, LessonUpdateFields } from "../../api/lesson";
  import TipexEditor from "./TipexEditor.svelte";
  import StudentSelector, { type StudentSelectorContext } from "./StudentSelector.svelte";
  import UserShareSelector, { type UserShareSelectorContext } from "./UserShareSelector.svelte";
  import { initializeDateTimeInput } from "$lib/utils/dateUtils";
  import { deleteLessonStudent, findLessonStudentByLessonAndStudent } from "../../api/lessonStudent";
  import { isLessonMinimized, toggleLessonMinimized } from "$lib/states/lessonMinimizedState.svelte";
  import { getCurrentUser } from "$lib/utils/auth";
  import { deleteUserLesson, updateUserLesson } from "../../api/userLesson";

  let { lessonId }: { lessonId: number } = $props();
  
  let lessonPromise = $derived(fetchLesson(lessonId));
  let isMinimized = $derived(isLessonMinimized(lessonId));
  
  let isEditing: boolean = $state(false);
  let showDeleteModal: boolean = $state(false);
  let showUnsubscribeModal: boolean = $state(false);

  // Current user state
  let currentUser: User | null = $state(null);
  let currentUserShare: UserLesson | null = $state(null);
  let userLoaded = $state(false);

  // This is a bit hacky, but I didn't have time to make a cleaner solution
  let { date: dateInput, time: timeInput } = $state(initializeDateTimeInput());
  let { date: copyToDate, time: copyToTime } = $state(initializeDateTimeInput());

  let plan: string = $state("");
  let concepts: string = $state("");
  let notes: string = $state("");
  let selectedStudents = $state<Student[]>([]);
  let studentSearchTerm = $state("");
  
  // Sharing state
  let selectedShares = $state<UserLesson[]>([]);
  let userSearchTerm = $state("");

  // Load current user once
  getCurrentUser().then(user => {
    currentUser = user;
    userLoaded = true;
  }).catch(() => {
    currentUser = null;
    userLoaded = true;
  });

  // Update form fields when lesson promise resolves
  $effect.pre(() => {
    lessonPromise.then(lesson => {
      if (lesson) {
        ({ date: dateInput, time: timeInput } = initializeDateTimeInput(lesson.datetime));
        plan = lesson.plan ?? "";
        concepts = lesson.concepts ?? "";
        notes = lesson.notes ?? "";
        selectedStudents = lesson.students || [];
        selectedShares = lesson.user_shares || [];
        
        // Find current user's share relationship
        if (currentUser && lesson.user_shares) {
          currentUserShare = lesson.user_shares.find(share => share.user_id === currentUser!.id) || null;
        }
      }
    }).catch(() => {
      // Error handling is done in the template with {#await}
    });
  });

  async function handleDelete() {
    const lesson = await lessonPromise;
    if (!lesson) return;
    await deleteLesson(lesson.id);
    removeLessonFromState(lesson.id);
    isEditing = false;
    showDeleteModal = false;
  }

  async function handleConfirm() {
    const lesson = await lessonPromise;
    if (!lesson) return;
    const datetime = new Date(`${dateInput}T${timeInput}`).toISOString();
    const updatedLesson : LessonUpdateFields = { ...lesson, datetime, plan, concepts, notes };
    const studentIds = selectedStudents.map(s => s.id);
    
    // Find students that were removed and delete their LessonStudent relationships
    const originalStudentIds = lesson.students?.map(s => s.id) || [];
    const removedStudentIds = originalStudentIds.filter(id => !studentIds.includes(id));
    
    if (removedStudentIds.length > 0) {
      try {
        // Find and delete each LessonStudent relationship by lesson_id and student_id
        await Promise.all(
          removedStudentIds.map(async (studentId) => {
            const lessonStudent = await findLessonStudentByLessonAndStudent(lesson.id, studentId);
            if (lessonStudent) {
              await deleteLessonStudent(lessonStudent.id);
            } else {
              console.warn(`LessonStudent relationship not found for lesson ${lesson.id} and student ${studentId}`);
            }
          })
        );
      } catch (error) {
        console.error("Error deleting lesson-student relationships:", error);
      }
    }
    
    // Update the lesson with new student list
    const updated = await updateLesson(lesson.id, updatedLesson, studentIds);
    updateLessonInState(updated);
    // Note: We can't update the lesson promise directly, but the parent state will be updated
    isEditing = false;
  }

  async function handleCancel() {
    const lesson = await lessonPromise;
    if (!lesson) return;
    isEditing = false;
    ({ date: dateInput, time: timeInput } = initializeDateTimeInput(lesson.datetime));
    plan = lesson.plan ?? "";
    concepts = lesson.concepts ?? "";
    notes = lesson.notes ?? "";
    selectedStudents = lesson.students || [];
    studentSearchTerm = "";
  }

  async function handleCopy() {
    const lesson = await lessonPromise;
    if (!lesson) return;
    const combinedDateTime = new Date(`${copyToDate}T${copyToTime}`).toISOString();

    const newLesson: LessonCreateFields = {
      ...lesson,
      datetime: combinedDateTime,
    };

    const studentIds = lesson.students?.map(s => s.id) || [];
    const createdLesson = await createLesson(newLesson, studentIds);
    addLessonToState(createdLesson);
  }

  // Simple stop sharing with confirmation
  async function handleStopSharingDirect() {
    if (!currentUserShare) {
      console.error('No current user share found');
      return;
    }
    
    try {
      await deleteUserLesson(currentUserShare.id);
      removeLessonFromState(lessonId);
      showUnsubscribeModal = false;
    } catch (error) {
      console.error('Failed to stop sharing:', error);
      alert('Failed to unsubscribe from lesson. Please try again.');
    }
  }

  // Update permission level for a shared user
  async function updateSharePermission(userId: number, permission: 'view' | 'edit' | 'manage') {
    try {
      const shareToUpdate = selectedShares.find(share => share.user_id === userId);
      if (shareToUpdate) {
        const updatedShare = await updateUserLesson(shareToUpdate.id, {
          permission_level: permission
        });
        
        // Update the local state
        selectedShares = selectedShares.map(share => 
          share.user_id === userId ? updatedShare : share
        );
        
        // Refresh the lesson data to update user_shares
        lessonPromise = fetchLesson(lessonId);
      }
    } catch (error) {
      console.error('Error updating permission:', error);
      alert('Failed to update permission. Please try again.');
    }
  }

  // Remove a user share
  async function removeShare(userId: number) {
    try {
      const shareToRemove = selectedShares.find(share => share.user_id === userId);
      if (shareToRemove) {
        await deleteUserLesson(shareToRemove.id);
        
        // Update local state
        selectedShares = selectedShares.filter(share => share.user_id !== userId);
        
        // Refresh the lesson data to update user_shares
        lessonPromise = fetchLesson(lessonId);
      }
    } catch (error) {
      console.error('Error removing share:', error);
      alert('Failed to remove share. Please try again.');
    }
  }

  function initializeDateTime(datetime: string) {
    return {
      date: new Date(datetime).toLocaleDateString("en-US"),
      time: new Date(datetime).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  }

  // Permission styling helper functions
  function getPermissionColor(permission: string): string {
    switch (permission) {
      case 'view': return 'badge-info';
      case 'edit': return 'badge-warning';
      case 'manage': return 'badge-error';
      default: return 'badge-neutral';
    }
  }

  function getPermissionLabel(permission: string): string {
    switch (permission) {
      case 'view': return 'View';
      case 'edit': return 'Edit';
      case 'manage': return 'Manage';
      default: return permission;
    }
  }

  // Helper functions to determine permissions given a lesson and current user
  function getUserPermission(lesson: Lesson): string | null {
    if (!currentUser || !userLoaded) return null;
    if (lesson && lesson.owner && lesson.owner.id === currentUser.id) return 'owner';
    
    // Check if user has a share relationship with this lesson
    if (lesson.user_shares) {
      const userShare = lesson.user_shares.find(share => share.user_id === currentUser!.id);
      if (userShare) return userShare.permission_level;
    }
    
    return null;
  }

  function canUserEdit(lesson: Lesson): boolean {
    const perm = getUserPermission(lesson);
    return perm === 'owner' || perm === 'edit' || perm === 'manage';
  }

  function canUserDelete(lesson: Lesson): boolean {
    const perm = getUserPermission(lesson);
    return perm === 'owner' || perm === 'manage';
  }

  function canUserCopy(lesson: Lesson): boolean {
    const perm = getUserPermission(lesson);
    return perm === 'owner' || perm === 'edit' || perm === 'manage';
  }

  function canUserManageSharing(lesson: Lesson): boolean {
    const perm = getUserPermission(lesson);
    return perm === 'owner' || perm === 'manage';
  }

  function hasLessonAccess(lesson: Lesson): boolean {
    const perm = getUserPermission(lesson);
    return perm !== null; // Has any access (owner, manage, edit, or view)
  }

  function isLessonSharedWithUser(lesson: Lesson): boolean {
    const perm = getUserPermission(lesson);
    return perm !== null && perm !== 'owner';
  }

  // Reusable permission dropdown snippet
  interface PermissionDropdownProps {
    onSelectView: () => void;
    onSelectEdit: () => void;
    onSelectManage: () => void;
  }
</script>

{#snippet permissionDropdownContent(props: PermissionDropdownProps)}
  <div tabindex="0" class="dropdown-content z-50 mt-1 bg-transparent flex flex-col p-0">
    <button
      type="button"
      class="badge badge-info text-xs px-3 py-2 cursor-pointer hover:outline-2 hover:outline-black hover:outline-offset-[-2px] transition-all shadow-md rounded-b-none w-20"
      onclick={props.onSelectView}
      title="Grant view-only access"
    >
      View
    </button>
    <button
      type="button"
      class="badge badge-warning text-xs px-3 py-2 cursor-pointer hover:outline-2 hover:outline-black hover:outline-offset-[-2px] transition-all shadow-md rounded-none w-20"
      onclick={props.onSelectEdit}
      title="Grant edit access"
    >
      Edit
    </button>
    <button
      type="button"
      class="badge badge-error text-xs px-3 py-2 cursor-pointer hover:outline-2 hover:outline-black hover:outline-offset-[-2px] transition-all shadow-md rounded-t-none w-20"
      onclick={props.onSelectManage}
      title="Grant manage access (can share with others)"
    >
      Manage
    </button>
  </div>
{/snippet}

{#await lessonPromise}
  <div class="w-full rounded-lg bg-neutral shadow-md p-4 space-y-4">
    <div class="flex justify-center items-center h-32">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  </div>
{:then lesson}
<div class="w-full rounded-lg bg-neutral shadow-md p-4 space-y-4">
  <!-- Action Buttons -->
  <div class="flex justify-between items-center">
    <!-- Left side - Minimize/Expand Toggle -->
    {#if !isEditing}
      <button 
        onclick={() => toggleLessonMinimized(lessonId)}
        class="btn btn-outline btn-sm group"
        title={isMinimized ? "Expand lesson" : "Minimize lesson"}
      >
        <img 
          src="/images/icons/{isMinimized ? 'chevron-down' : 'minus-sign'}.svg" 
          alt={isMinimized ? "Expand" : "Minimize"} 
          class="w-4 h-4 group-hover:filter group-hover:brightness-0 group-hover:invert" 
        />
      </button>
    {:else}
      <!-- Spacer when editing to maintain layout -->
      <div></div>
    {/if}

    <!-- Right side - Action buttons -->
    <div class="flex space-x-2">
      {#if isEditing}
        <button onclick={handleConfirm} class="btn btn-success btn-sm">Confirm</button>
        <button onclick={handleCancel} class="btn btn-warning btn-sm">Cancel</button>
        {#if canUserDelete(lesson)}
          <button onclick={() => showDeleteModal = true} class="btn btn-error btn-sm">
            <img src="/images/icons/trash3.svg" alt="Trash Icon" class="w-4 h-4" />
          </button>
        {/if}
      {:else if !isMinimized}
        <!-- Copy button - only show if user can copy -->
        {#if canUserCopy(lesson)}
          <div class="dropdown">
            <button tabindex="0" class="btn btn-info btn-sm">
              <img src="/images/icons/arrow-clockwise.svg" alt="Copy Icon" class="w-4 h-4" />
            </button>
            <div class="dropdown-content bg-neutral p-4 rounded-lg shadow-md">
              <input type="date" bind:value={copyToDate} class="input input-bordered w-full mb-2" />
              <input type="time" bind:value={copyToTime} class="input input-bordered w-full mb-2" />
              <button onclick={handleCopy} class="btn btn-success btn-sm w-full">Confirm</button>
            </div>
          </div>
        {/if}
        
        <!-- Edit button - only show if user can edit -->
        {#if canUserEdit(lesson)}
          <button onclick={() => isEditing = true} class="btn btn-accent btn-sm">
            <img src="/images/icons/pencil-fill.svg" alt="Edit Icon" class="w-4 h-4" />
          </button>
        {/if}
        
        <!-- Delete button - only show if user can delete -->
        {#if canUserDelete(lesson)}
          <button onclick={() => showDeleteModal = true} class="btn btn-error btn-sm">
            <img src="/images/icons/trash3.svg" alt="Trash Icon" class="w-4 h-4" />
          </button>
        {/if}
        
        <!-- Stop sharing button - only show if this is a shared lesson -->
        {#if isLessonSharedWithUser(lesson)}
          <button onclick={() => showUnsubscribeModal = true} class="btn btn-warning btn-sm" title="Stop receiving this shared lesson">
            ×
          </button>
        {/if}
      {/if}
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  {#if showDeleteModal}
    <dialog class="modal modal-open" aria-modal="true" aria-labelledby="delete-modal-title">
      <div class="modal-box">
        <h3 id="delete-modal-title" class="font-bold text-lg">Confirm Deletion</h3>
        <p class="py-4">Are you sure you want to delete this lesson?</p>
        <div class="modal-action">
          <button onclick={handleDelete} class="btn btn-error">Delete</button>
          <button onclick={() => showDeleteModal = false} class="btn">Cancel</button>
        </div>
      </div>
    </dialog>
  {/if}

  <!-- Unsubscribe Confirmation Modal -->
  {#if showUnsubscribeModal}
    <dialog class="modal modal-open" aria-modal="true" aria-labelledby="unsubscribe-modal-title">
      <div class="modal-box">
        <h3 id="unsubscribe-modal-title" class="font-bold text-lg">Unsubscribe from Shared Lesson</h3>
        <p class="py-4">
          Are you sure you want to unsubscribe from this shared lesson? 
          <br><br>
          <strong>You will no longer have access to:</strong>
        </p>
        <ul class="list-disc list-inside py-2 text-sm opacity-80">
          <li>View the lesson content</li>
          <li>Edit the lesson (if you had edit permissions)</li>
          <li>See the lesson in your lesson list</li>
        </ul>
        <p class="text-sm opacity-70 mt-2">
          The lesson owner can share it with you again if needed.
        </p>
        <div class="modal-action">
          <button onclick={handleStopSharingDirect} class="btn btn-warning">Unsubscribe</button>
          <button onclick={() => showUnsubscribeModal = false} class="btn">Keep Access</button>
        </div>
      </div>
    </dialog>
  {/if}

  {#if isMinimized && !isEditing}
    <!-- Minimized View -->
    {@const { date, time } = initializeDateTime(lesson.datetime)}
    
    <div class="flex items-center bg-neutral p-3 rounded-lg shadow-sm h-16 overflow-hidden">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <p class="text-sm font-medium text-secondary">{time}</p>
          <div class="text-xs text-secondary opacity-70">•</div>
          <p class="text-xs text-secondary opacity-70 truncate">{date}</p>
        </div>
        {#if lesson.students && lesson.students.length > 0}
          <div class="relative w-full h-5 overflow-hidden">
            <div class="absolute inset-0 flex gap-1 overflow-x-auto" style="scrollbar-width: none; -ms-overflow-style: none;">
              {#each lesson.students as student}
                <span class="text-xs bg-secondary text-secondary-content px-2 py-0.5 rounded-full whitespace-nowrap flex-shrink-0">
                  {student.first_name}
                </span>
              {/each}
            </div>
          </div>
        {:else}
          <p class="text-xs text-secondary opacity-50 italic">No students assigned</p>
        {/if}
      </div>
    </div>
  {:else}
    <!-- Full View -->
    
    <!-- Date Section -->
    {#if isEditing}
      <input type="date" bind:value={dateInput} class="input input-bordered w-36" />
      <input type="time" bind:value={timeInput} class="input input-bordered w-28" />
    {:else}
      {@const { date, time } = initializeDateTime(lesson.datetime)}
      {@const weekday = new Date(lesson.datetime).toLocaleDateString("en-US", { weekday: "long" })}
      <div class="card-body flex items-center justify-between bg-neutral rounded-lg shadow-sm">
        <div>
          <p class="text-lg font-semibold text-secondary">{weekday}</p>
            <div class="flex items-center gap-2 mb-1">
              <p class="text-sm font-medium text-secondary">{time}</p>
              <div class="text-xs text-secondary opacity-70">•</div>
              <p class="text-xs text-secondary opacity-70 truncate">{date}</p>
            </div>
        </div>
        
        <!-- Shared lesson indicator -->
        {#if isLessonSharedWithUser(lesson) && currentUserShare}
          <div class="flex items-center gap-2">
            <span class="badge badge-outline badge-sm">
              Shared - {getPermissionLabel(currentUserShare.permission_level)}
            </span>
          </div>
        {/if}
      </div>
    {/if}

    <!-- Students Section -->
    <StudentSelector 
      bind:selectedStudents={selectedStudents}
      bind:studentSearchTerm={studentSearchTerm}
      isEditing={isEditing}
    >
      {#snippet children(ctx: StudentSelectorContext)}
        <!-- Selected Students Display (shows in both editing and view mode) -->
        <div class="bg-neutral shadow-md rounded-lg min-h-24 mt-2 card-body">
          <h2 class="mb-2 card-title text-secondary">
            {#if ctx.selectedStudents.length <= 1}
              {ctx.selectedStudents.length === 1 ? 'Student' : 'Students'}
            {:else}
              Students ({ctx.selectedStudents.length})
            {/if}
          </h2>
          
          {#if ctx.isEditing}
            <!-- Editing Mode - Student Selection Interface -->
            <div class="flex flex-col space-y-2 mb-4">
              <label class="label" for="lesson-card-student-search">
                <span class="label-text text-secondary">Add Students</span>
              </label>
              
              <!-- Student Search Input -->
              <div class="relative">
                <input
                  id="lesson-card-student-search"
                  type="text"
                  placeholder="Search students..."
                  bind:value={studentSearchTerm}
                  oninput={ctx.handleStudentSearch}
                  onfocus={() => ctx.showStudentDropdown = studentSearchTerm.length > 0}
                  onblur={() => {
                    setTimeout(() => ctx.showStudentDropdown = false, 150);
                  }}
                  class="input input-bordered w-full bg-neutral text-secondary border-secondary"
                />
                
                <!-- Student Dropdown -->
                {#if ctx.showStudentDropdown}
                  <div class="absolute z-50 w-full mt-1 bg-neutral border border-secondary rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {#if ctx.filteredStudents.length > 0}
                      {#each ctx.filteredStudents as student (student.id)}
                        <button
                          type="button"
                          class="w-full px-4 py-2 text-left hover:bg-secondary hover:text-neutral transition-colors text-secondary"
                          onclick={() => ctx.addStudent(student)}
                        >
                          {student.first_name} {student.last_name || ''}
                        </button>
                      {/each}
                    {:else}
                      <div class="px-4 py-2 text-sm text-secondary opacity-60">
                        No students found matching "{studentSearchTerm}"
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
            </div>
          {/if}
          
          {#if ctx.selectedStudents.length > 0}
            <div class="flex flex-wrap gap-2">
              {#each ctx.selectedStudents as student (student.id)}
                {#if ctx.isEditing}
                  <button
                    type="button"
                    class="flex items-center gap-1 bg-neutral shadow-md hover:bg-error hover:text-error-content rounded-full px-3 py-1 text-sm transition-colors cursor-pointer"
                    onclick={() => ctx.removeStudent(student.id)}
                    aria-label="Remove {student.first_name} {student.last_name || ''}"
                    title="Click to remove"
                  >
                    <span class="truncate max-w-32 text-secondary">{student.first_name} {student.last_name || ''}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 flex-shrink-0 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                {:else}
                  <a
                    href="/students/{student.id}"
                    target="_blank"
                    class="bg-neutral shadow-md rounded-full px-3 py-1 text-sm hover:bg-gray-100 transition-colors cursor-pointer block"
                  >
                    <span class="truncate max-w-32 text-secondary">{student.first_name} {student.last_name || ''}</span>
                  </a>
                {/if}
              {/each}
            </div>
          {:else}
            <div class="text-sm text-secondary opacity-60 italic flex items-center">
              {ctx.isEditing ? 'No students selected for this lesson' : 'No students assigned to this lesson'}
            </div>
          {/if}
        </div>
      {/snippet}
    </StudentSelector>

    <!-- Plan Section -->
    <div class="card bg-neutral shadow-md">
      {#if isEditing}
        <TipexEditor
          bind:body={plan}
          heading="Today's Plan"
        />
      {:else}
        <div class="card-body">
          <h2 class="card-title text-secondary">Today's Plan</h2>
          <div class="rich-editor">{@html plan}</div>
        </div>
      {/if}
    </div>

    <!-- Concepts Taught Section -->
    <div class="card bg-neutral shadow-md">
      {#if isEditing}
        <TipexEditor 
          bind:body={concepts}
          heading="Concepts Taught"
        />
      {:else}
        <div class="card-body">
          <h2 class="card-title text-secondary">Concepts Taught</h2>
          <div class="rich-editor">{@html concepts}</div>
        </div>
      {/if}
    </div>

    <!-- Notes Section -->
    <div class="card bg-neutral shadow-md">
      {#if isEditing}
        <TipexEditor 
          bind:body={notes}
          heading="Lesson Notes"
        />
      {:else}
        <div class="card-body">
          <h2 class="card-title text-secondary">Lesson Notes</h2>
          <div class="rich-editor">{@html notes}</div>
        </div>
      {/if}
    </div>

    <!-- Lesson Access Section - show to anyone with lesson access -->
    {#if hasLessonAccess(lesson)}
      <div class="bg-neutral shadow-md rounded-lg min-h-24 mt-2 card-body">
        <h2 class="mb-2 card-title text-secondary">Who Can See This Lesson</h2>
        
        <div class="flex flex-wrap gap-2">
          <!-- Show lesson owner first -->
          {#if lesson.owner}
            <div class="bg-neutral shadow-md rounded-full px-3 py-1 text-sm flex items-center gap-1">
              <span class="truncate max-w-32 text-secondary">
                {lesson.owner.id === currentUser?.id ? 'You' : `${lesson.owner.first_name} ${lesson.owner.last_name}`}
              </span>
              <span class="badge badge-xs badge-primary">Owner</span>
            </div>
          {/if}
          
          <!-- Show shared users -->
          {#if selectedShares.length > 0}
            {#each selectedShares as share (share.id)}
              {@const user = share.user}
              {#if user}
                <div class="bg-neutral shadow-md rounded-full px-3 py-1 text-sm flex items-center gap-1">
                  <span class="truncate max-w-32 text-secondary">
                    {user.id === currentUser?.id ? 'You' : `${user.first_name} ${user.last_name}`}
                  </span>
                  
                  <!-- Show permission dropdown if user can manage sharing and is editing -->
                  {#if canUserManageSharing(lesson) && isEditing}
                    <div class="dropdown dropdown-end">
                      <button
                        type="button"
                        tabindex="0"
                        role="button"
                        class="badge badge-xs {getPermissionColor(share.permission_level)} cursor-pointer hover:opacity-80"
                      >
                        {getPermissionLabel(share.permission_level)} ▾
                      </button>
                      {@render permissionDropdownContent({
                        onSelectView: () => updateSharePermission(share.user_id, 'view'),
                        onSelectEdit: () => updateSharePermission(share.user_id, 'edit'),
                        onSelectManage: () => updateSharePermission(share.user_id, 'manage')
                      })}
                    </div>
                    <button
                      type="button"
                      class="btn btn-xs btn-circle btn-ghost text-error hover:bg-error hover:text-error-content"
                      onclick={() => removeShare(share.user_id)}
                      title="Remove share"
                    >
                      ×
                    </button>
                  {:else}
                    <span class="badge badge-xs {getPermissionColor(share.permission_level)}">
                      {getPermissionLabel(share.permission_level)}
                    </span>
                  {/if}
                </div>
              {/if}
            {/each}
          {/if}
        </div>
        
        <!-- Show management options only if user can manage sharing and is editing -->
        {#if canUserManageSharing(lesson) && isEditing}
          <div class="mt-4 pt-4 border-t border-secondary/20">
            <UserShareSelector 
              lessonId={lessonId}
              bind:selectedShares={selectedShares}
              bind:userSearchTerm={userSearchTerm}
              isEditing={true}
            >
              {#snippet children(ctx: UserShareSelectorContext)}
                <div class="flex flex-col space-y-2">
                  <label class="label" for="lesson-card-user-search">
                    <span class="label-text text-secondary">Share with more users</span>
                  </label>
                  
                  <!-- User Search Input -->
                  <div class="relative">
                    <input
                      id="lesson-card-user-search"
                      type="text"
                      placeholder="Search users..."
                      bind:value={userSearchTerm}
                      oninput={ctx.handleUserSearch}
                      onfocus={() => ctx.showUserDropdown = userSearchTerm.length > 0}
                      onblur={() => {
                        setTimeout(() => ctx.showUserDropdown = false, 150);
                      }}
                      class="input input-bordered w-full bg-neutral text-secondary border-secondary"
                    />
                    
                    <!-- User Dropdown -->
                    {#if ctx.showUserDropdown}
                      <div class="absolute z-50 w-full mt-1 bg-neutral border border-secondary rounded-lg shadow-lg max-h-64 overflow-y-auto">
                        {#if ctx.filteredUsers.length > 0}
                          {#each ctx.filteredUsers as user (user.id)}
                            <div class="px-4 py-3 text-secondary border-b border-secondary/20 last:border-0 flex items-center justify-between gap-3">
                              <div class="flex-1 min-w-0">
                                <div class="font-medium text-base">{user.first_name} {user.last_name}</div>
                                <div class="text-xs opacity-70">{user.email}</div>
                              </div>
                              <div class="dropdown dropdown-end">
                                <button
                                  type="button"
                                  tabindex="0"
                                  role="button"
                                  class="btn btn-sm btn-primary"
                                >
                                  +
                                </button>
                                {@render permissionDropdownContent({
                                  onSelectView: () => ctx.addUser(user, 'view'),
                                  onSelectEdit: () => ctx.addUser(user, 'edit'),
                                  onSelectManage: () => ctx.addUser(user, 'manage')
                                })}
                              </div>
                            </div>
                          {/each}
                        {:else}
                          <div class="px-4 py-2 text-sm text-secondary opacity-60">
                            No users found matching "{userSearchTerm}"
                          </div>
                        {/if}
                      </div>
                    {/if}
                  </div>
                </div>
              {/snippet}
            </UserShareSelector>
          </div>
        {/if}
      </div>
    {/if}
  {/if}
</div>
{:catch error}
  <div class="w-full rounded-lg bg-error shadow-md p-4 space-y-4">
    <div class="text-error-content">
      <h3 class="font-bold text-lg">Error loading lesson</h3>
      <p>{error.message || 'Failed to fetch lesson'}</p>
    </div>
  </div>
{/await}


