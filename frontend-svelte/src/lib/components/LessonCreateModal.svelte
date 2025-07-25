<script lang="ts">
  import { createLesson } from "../../api/lesson";
  import type { LessonCreateFields } from "../../api/lesson";
  import type { Lesson, Student } from "../../types";
  import { lessonState, addLessonToState } from "$lib/states/lessonState.svelte";
  import { lessonWeekStartDate } from "$lib/states/lessonWeekStartDate.svelte";
  import TipexEditor from "./TipexEditor.svelte";
  import StudentSelector from "./StudentSelector.svelte";

  let { children } = $props();

  let date = $state("");
  let time = $state("");
  let plan = $state("");
  let concepts = $state("");
  let notes = $state("");

  // Student selection state
  let selectedStudents = $state<Student[]>([]);
  let studentSearchTerm = $state("");

  let lessonCreateModal: HTMLDialogElement;
  let dateWarning = $state(false);
  let timeWarning = $state(false);

  // Reset form state
  function resetForm() {
    date = "";
    time = "";
    plan = "";
    concepts = "";
    notes = "";
    selectedStudents = [];
    studentSearchTerm = "";
    dateWarning = false;
    timeWarning = false;
  }

  // Close modal and reset form
  function closeModal() {
    resetForm();
    lessonCreateModal.close();
  }

  async function handleCreateLesson() {
    dateWarning = date === "";
    timeWarning = time === "";

    if (dateWarning || timeWarning) {
      return;
    }

    const datetime = new Date(`${date}T${time}`).toISOString();
    const newLesson: LessonCreateFields = {
      datetime,
      plan,
      concepts,
      notes,
    };

    try {
      const studentIds = selectedStudents.map(s => s.id);
      const createdLesson = await createLesson(newLesson, studentIds);
      addLessonToState(createdLesson);
      resetForm();
      lessonCreateModal.close();
    } catch (error) {
      console.error("Error creating lesson:", error);
    }
  }
</script>

<button
  class="btn btn-secondary"
  onclick={async () => {
    resetForm();
    lessonCreateModal.showModal();
  }}
>
  {@render children?.()}
</button>
<dialog bind:this={lessonCreateModal} class="modal">
  <div class="modal-box bg-base-100 w-full max-w-4xl">
    <h3 class="text-lg font-bold text-base-content">Create a New Lesson</h3>
    <div class="py-4 flex flex-col space-y-4">
      <div class="flex flex-row space-x-4 w-full">
        <div class="flex flex-col space-y-4 w-1/2">
          <label class="label" for="date">
            <span class="label-text">Date</span>
          </label>
          <input
            id="date"
            type="date"
            bind:value={date}
            class="input input-bordered w-full bg-secondary"
            required
          />
          {#if dateWarning}
            <p class="text-error">Date is required.</p>
          {/if}
        </div>
        <div class="flex flex-col space-y-4 w-1/2">
          <label class="label" for="time">
            <span class="label-text">Time</span>
          </label>
          <input
            id="time"
            type="time"
            bind:value={time}
            class="input input-bordered w-full bg-secondary"
            required
          />
          {#if timeWarning}
            <p class="text-error">Time is required.</p>
          {/if}
        </div>
      </div>
      <div class="flex flex-row space-x-4 w-full">
        <div class="flex flex-col space-y-4 w-1/2">
          <TipexEditor
            bind:body={plan}
            heading="Today's Plan"
            height="h-[20vh]"
          />
        </div>
        <div class="flex flex-col space-y-4 w-1/2">
          <TipexEditor
            bind:body={concepts}
            heading="Concepts Taught"
            height="h-[20vh]"
          />
        </div>
      </div>
      <div class="flex flex-row space-x-4 w-full">
        <div class="flex flex-col space-y-4 w-1/2">
          <TipexEditor
            bind:body={notes}
            heading="Lesson Notes"
            height="h-[20vh]"
          />
        </div>
        <div class="flex flex-col space-y-4 w-1/2">
          <!-- Student Selection Section -->
          <StudentSelector 
            bind:selectedStudents={selectedStudents}
            bind:studentSearchTerm={studentSearchTerm}
            isEditing={true}
          >
            {#snippet children(ctx)}
              <div class="flex flex-col space-y-2">
                <label class="label" for="student-search">
                  <span class="label-text">Students</span>
                </label>
                
                <!-- Student Search Input -->
                <div class="relative">
                  <input
                    id="student-search"
                    type="text"
                    placeholder="Search students by name..."
                    bind:value={studentSearchTerm}
                    oninput={ctx.handleStudentSearch}
                    onfocus={() => ctx.showStudentDropdown = studentSearchTerm.length > 0}
                    onblur={() => {
                      setTimeout(() => ctx.showStudentDropdown = false, 150);
                    }}
                    class="input input-bordered w-full bg-secondary"
                  />
                  
                  <!-- Student Dropdown -->
                  {#if ctx.showStudentDropdown}
                    <div class="absolute z-50 w-full mt-1 bg-base-100 border border-base-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                      {#if ctx.filteredStudents.length > 0}
                        {#each ctx.filteredStudents as student (student.id)}
                          <button
                            type="button"
                            class="w-full px-4 py-2 text-left hover:bg-base-200 transition-colors"
                            onclick={() => ctx.addStudent(student)}
                          >
                            {student.first_name} {student.last_name || ''}
                          </button>
                        {/each}
                      {:else}
                        <div class="px-4 py-2 text-sm text-base-content opacity-60">
                          No students found matching "{studentSearchTerm}"
                        </div>
                      {/if}
                    </div>
                  {/if}
                </div>
                
                <!-- Selected Students List -->
                {#if ctx.selectedStudents.length > 0}
                  <div class="bg-base-200 rounded-lg p-3 min-h-24">
                    <span class="text-sm font-medium mb-2 block">Selected Students ({ctx.selectedStudents.length}):</span>
                    <div class="flex flex-wrap gap-2">
                      {#each ctx.selectedStudents as student (student.id)}
                        <button
                          type="button"
                          class="flex items-center gap-1 bg-base-100 hover:bg-error hover:text-error-content rounded-full px-3 py-1 text-sm transition-colors cursor-pointer"
                          onclick={() => ctx.removeStudent(student.id)}
                          aria-label="Remove {student.first_name} {student.last_name || ''}"
                          title="Click to remove"
                        >
                          <span class="truncate max-w-32">{student.first_name} {student.last_name || ''}</span>
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 flex-shrink-0 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      {/each}
                    </div>
                  </div>
                {:else}
                  <div class="text-sm text-base-content opacity-60 italic min-h-24 flex items-center">
                    No students selected for this lesson
                  </div>
                {/if}
              </div>
            {/snippet}
          </StudentSelector>
        </div>
      </div>
    </div>
    <div class="modal-action">
      <button class="btn" onclick={closeModal}>Cancel</button>
      <button class="btn btn-primary" onclick={handleCreateLesson}>Create</button>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button onclick={closeModal}>close</button>
  </form>
</dialog>
