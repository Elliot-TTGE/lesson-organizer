<script lang="ts">
  import type { Lesson, Student } from "../../types";
  import { deleteLesson, updateLesson, createLesson, fetchLesson } from "../../api/lesson";
  import { addLessonToState, lessonState, removeLessonFromState, updateLessonInState } from "$lib/states/lessonState.svelte";
  import type { LessonCreateFields, LessonUpdateFields } from "../../api/lesson";
  import TipexEditor from "./TipexEditor.svelte";
  import StudentSelector, { type StudentSelectorContext } from "./StudentSelector.svelte";
  import { initializeDateTimeInput } from "$lib/utils/dateUtils";
  import { deleteLessonStudent, findLessonStudentByLessonAndStudent } from "../../api/lessonStudent";
  import { isLessonMinimized, toggleLessonMinimized } from "$lib/states/lessonMinimizedState.svelte";

  let { lessonId }: { lessonId: number } = $props();
  
  let lessonPromise = $derived(fetchLesson(lessonId));
  let isMinimized = $derived(isLessonMinimized(lessonId));
  
  let isEditing: boolean = $state(false);
  let showDeleteModal: boolean = $state(false);

  // This is a bit hacky, but I didn't have time to make a cleaner solution
  let { date: dateInput, time: timeInput } = $state(initializeDateTimeInput());
  let { date: copyToDate, time: copyToTime } = $state(initializeDateTimeInput());

  let plan: string = $state("");
  let concepts: string = $state("");
  let notes: string = $state("");
  let selectedStudents = $state<Student[]>([]);
  let studentSearchTerm = $state("");

  // Update form fields when lesson promise resolves
  $effect.pre(() => {
    lessonPromise.then(lesson => {
      if (lesson) {
        ({ date: dateInput, time: timeInput } = initializeDateTimeInput(lesson.datetime));
        plan = lesson.plan ?? "";
        concepts = lesson.concepts ?? "";
        notes = lesson.notes ?? "";
        selectedStudents = lesson.students || [];
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

  function initializeDateTime(datetime: string) {
    return {
      date: new Date(datetime).toLocaleDateString("en-US"),
      time: new Date(datetime).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  }
</script>

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
        class="btn btn-outline btn-sm"
        title={isMinimized ? "Expand lesson" : "Minimize lesson"}
      >
        <img 
          src="/images/icons/{isMinimized ? 'chevron-down' : 'minus-sign'}.svg" 
          alt={isMinimized ? "Expand" : "Minimize"} 
          class="w-4 h-4" 
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
        <button onclick={() => showDeleteModal = true} class="btn btn-error btn-sm">
          <img src="/images/icons/trash3.svg" alt="Trash Icon" class="w-4 h-4" />
        </button>
      {:else if !isMinimized}
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
        <button onclick={() => isEditing = true} class="btn btn-accent btn-sm">
          <img src="/images/icons/pencil-fill.svg" alt="Edit Icon" class="w-4 h-4" />
        </button>
        <button onclick={() => showDeleteModal = true} class="btn btn-error btn-sm">
          <img src="/images/icons/trash3.svg" alt="Trash Icon" class="w-4 h-4" />
        </button>
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

  {#if isMinimized && !isEditing}
    <!-- Minimized View -->
    {@const { date, time } = initializeDateTime(lesson.datetime)}
    {@const weekday = new Date(lesson.datetime).toLocaleDateString("en-US", { weekday: "short" })}
    
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
      <div class="flex items-center justify-between bg-neutral p-4 rounded-lg shadow-sm">
        <div>
          <p class="text-lg font-semibold text-secondary">{weekday}</p>
            <div class="flex items-center gap-2 mb-1">
              <p class="text-sm font-medium text-secondary">{time}</p>
              <div class="text-xs text-secondary opacity-70">•</div>
              <p class="text-xs text-secondary opacity-70 truncate">{date}</p>
            </div>
        </div>
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
        <div class="bg-neutral shadow-md rounded-lg p-3 min-h-24 mt-2">
          <span class="text-lg font-medium mb-2 block text-secondary">
            {#if ctx.selectedStudents.length <= 1}
              {ctx.selectedStudents.length === 1 ? 'Student' : 'Students'}
            {:else}
              Students ({ctx.selectedStudents.length})
            {/if}
          </span>
          
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
                  placeholder="Search students by name..."
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
