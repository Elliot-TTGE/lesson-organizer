<script lang="ts">
    import { type Student } from "../../types";
    import { fetchStudent, updateStudent } from "../../api/student";
    import { createStudentStatusHistory, deleteStudentStatusHistory } from "../../api/studentStatusHistory";
    import { createStudentLevelHistory, deleteStudentLevelHistory } from "../../api/studentLevelHistory";
    import { onMount } from "svelte";
    import { 
        getLatestLevelId, 
        getLatestStatusId, 
        getLastLessonFromStudent, 
        getNextLessonFromStudent,
        formatLessonDateTime, 
        getStudentFullName,
        formatStudentDate 
    } from "../utils";
    import { 
        statusState, 
        refreshStatuses, 
        getStatusNameById,
        levelState,
        refreshLevels,
        getLevelDisplayById
    } from "../states";
    import TipexEditor from "./TipexEditor.svelte";
    import LessonCard from "./LessonCard.svelte";
    import LoadingState from "./LoadingState.svelte";
    import StatCard from "./StatCard.svelte";
    import NumberCounter from "./NumberCounter.svelte";
    import HistoryTimeline from "./HistoryTimeline.svelte";
    import EditableField from "./EditableField.svelte";

    let { studentId, onStudentUpdated } = $props<{ 
        studentId: number; 
        onStudentUpdated?: (student: Student) => void;
    }>();

    let student = $state<Student | null>(null);
    let isLoading = $state(true);
    let error = $state<string | null>(null);
    let isUpdatingStatus = $state(false);
    let isUpdatingLevel = $state(false);
    let isUpdatingClassesPerWeek = $state(false);
    let isUpdatingStartDate = $state(false);
    let isUpdatingName = $state(false);
    let deletingStatusId = $state<number | null>(null);
    let deletingLevelId = $state<number | null>(null);
    let isEditingName = $state(false);
    let editingFirstName = $state('');
    let editingLastName = $state('');

    // ===== LIFECYCLE =====
    onMount(async () => {
        try {
            // Fetch student data and ensure states are loaded
            const [fetchedStudent] = await Promise.all([
                fetchStudent(studentId),
                // Ensure states are loaded (these are no-op if already loaded)
                statusState.statuses.length === 0 ? refreshStatuses() : Promise.resolve(),
                levelState.levels.length === 0 ? refreshLevels() : Promise.resolve()
            ]);
            
            student = fetchedStudent;
            
            isLoading = false;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to fetch student data';
            isLoading = false;
        }
    });

    // ===== BASIC STUDENT FIELD UPDATES =====
    async function handleNameChange(firstName: string, lastName: string) {
        if (!student || isUpdatingName) return;
        
        isUpdatingName = true;
        try {
            // Update student in database
            const updatedStudent = await updateStudent(student.id, {
                first_name: firstName,
                last_name: lastName
            });

            // Update local student data
            student.first_name = updatedStudent.first_name;
            student.last_name = updatedStudent.last_name;
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update name';
        } finally {
            isUpdatingName = false;
        }
    }

    async function handleStartDateChange(newStartDate: string) {
        if (!student || isUpdatingStartDate) return;
        
        isUpdatingStartDate = true;
        try {
            // If it's just a date string (YYYY-MM-DD), convert to ISO string
            const dateValue = newStartDate.includes('T') ? newStartDate : new Date(newStartDate + 'T00:00:00').toISOString();
            
            // Update student in database
            const updatedStudent = await updateStudent(student.id, {
                date_started: dateValue
            });

            // Update local student data
            student.date_started = updatedStudent.date_started;
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update start date';
        } finally {
            isUpdatingStartDate = false;
        }
    }

    async function handleClassesPerWeekChange(newClassesPerWeek: number) {
        if (!student || isUpdatingClassesPerWeek || newClassesPerWeek < 0) return;
        
        isUpdatingClassesPerWeek = true;
        try {
            // Update student in database
            const updatedStudent = await updateStudent(student.id, {
                classes_per_week: newClassesPerWeek
            });

            // Update local student data
            student.classes_per_week = updatedStudent.classes_per_week;
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update classes per week';
        } finally {
            isUpdatingClassesPerWeek = false;
        }
    }

    // ===== NAME EDITING HELPERS =====
    function startEditingName() {
        if (!student) return;
        editingFirstName = student.first_name;
        editingLastName = student.last_name || '';
        isEditingName = true;
    }

    function cancelEditingName() {
        isEditingName = false;
        editingFirstName = '';
        editingLastName = '';
    }

    async function saveNameChanges() {
        if (!student || !editingFirstName.trim()) return;
        
        await handleNameChange(editingFirstName.trim(), editingLastName.trim());
        isEditingName = false;
        editingFirstName = '';
        editingLastName = '';
    }

    // ===== STATUS HISTORY MANAGEMENT =====
    async function handleStatusChange(newStatusId: number) {
        if (!student || isUpdatingStatus) return;
        
        isUpdatingStatus = true;
        try {
            // Create new status history entry
            const newStatusHistory = await createStudentStatusHistory({
                student_id: student.id,
                status_id: newStatusId,
                changed_at: new Date().toISOString()
            });

            // Update local student data
            student.status_history = [...(student.status_history || []), newStatusHistory];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update status';
        } finally {
            isUpdatingStatus = false;
        }
    }

    async function handleDeleteStatusHistory(statusHistoryId: number) {
        if (!student || deletingStatusId) return;
        
        deletingStatusId = statusHistoryId;
        try {
            // Delete from database
            await deleteStudentStatusHistory(statusHistoryId);

            // Update local student data by filtering out the deleted entry
            student.status_history = student.status_history?.filter(sh => sh.id !== statusHistoryId) || [];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to delete status history';
        } finally {
            deletingStatusId = null;
        }
    }

    // ===== LEVEL HISTORY MANAGEMENT =====
    async function handleLevelChange(newLevelId: number) {
        if (!student || isUpdatingLevel) return;
        
        isUpdatingLevel = true;
        try {
            // Create new level history entry
            const newLevelHistory = await createStudentLevelHistory({
                student_id: student.id,
                level_id: newLevelId,
                start_date: new Date().toISOString()
            });

            // Update local student data
            student.level_history = [...(student.level_history || []), newLevelHistory];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to update level';
        } finally {
            isUpdatingLevel = false;
        }
    }

    async function handleDeleteLevelHistory(levelHistoryId: number) {
        if (!student || deletingLevelId) return;
        
        deletingLevelId = levelHistoryId;
        try {
            // Delete from database
            await deleteStudentLevelHistory(levelHistoryId);

            // Update local student data by filtering out the deleted entry
            student.level_history = student.level_history?.filter(lh => lh.id !== levelHistoryId) || [];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to delete level history';
        } finally {
            deletingLevelId = null;
        }
    }

    // ===== NOTES MANAGEMENT =====
    async function saveNotesField(field: 'notes_general' | 'notes_strengths' | 'notes_weaknesses' | 'notes_future', content: string) {
        if (!student) return;
        
        try {
            // Update student in database
            const updatedStudent = await updateStudent(student.id, {
                [field]: content
            });

            // Update local student data
            student[field] = updatedStudent[field];
            
            // Notify parent component
            if (onStudentUpdated) {
                onStudentUpdated(student);
            }
        } catch (err) {
            error = err instanceof Error ? err.message : `Failed to update ${field}`;
            throw err; // Re-throw to let TipexEditor handle the error
        }
    }

    const saveGeneralNotes = async (content: string) => saveNotesField('notes_general', content);
    const saveFutureNotes = async (content: string) => saveNotesField('notes_future', content);
    const saveStrengthsNotes = async (content: string) => saveNotesField('notes_strengths', content);
    const saveWeaknessesNotes = async (content: string) => saveNotesField('notes_weaknesses', content);

    // ===== UTILITY FUNCTIONS =====
    function handleUpdate() {
        // This would be called when student data is updated in the modal
        // For now, we'll just refresh the data
        if (student && onStudentUpdated) {
            onStudentUpdated(student);
        }
    }

    // ===== COMPUTED VALUES =====
    const currentStatusDisplay = $derived(() => {
        if (!student) return '-';
        
        const latestStatusId = getLatestStatusId(student);
        if (!latestStatusId) {
            return '-';
        }

        return getStatusNameById(latestStatusId) ?? '-';
    });

    const lastLessonDisplay = $derived(() => {
        if (!student) return '-';
        
        const lastLesson = getLastLessonFromStudent(student);
        return lastLesson ? formatLessonDateTime(lastLesson) : '-';
    });

    const nextLessonDisplay = $derived(() => {
        if (!student) return '-';
        
        const nextLesson = getNextLessonFromStudent(student);
        return nextLesson ? formatLessonDateTime(nextLesson) : '-';
    });

    const currentLevelDisplay = $derived(() => {
        if (!student) return 'Not set';
        
        const latestLevelId = getLatestLevelId(student);
        if (!latestLevelId) {
            return 'Not set';
        }

        return getLevelDisplayById(latestLevelId) ?? 'Not set';
    });

    const latestStatusId = $derived(() => student ? getLatestStatusId(student) : null);
    const latestLevelId = $derived(() => student ? getLatestLevelId(student) : null);

    // Prepare data for HistoryTimeline components
    const statusHistoryItems = $derived(() => {
        if (!student?.status_history) return [];
        return student.status_history.map(sh => ({
            id: sh.id,
            date: sh.changed_at,
            displayText: getStatusNameById(sh.status_id) ?? 'Unknown Status'
        }));
    });

    const levelHistoryItems = $derived(() => {
        if (!student?.level_history) return [];
        return student.level_history.map(lh => ({
            id: lh.id,
            date: lh.start_date,
            displayText: getLevelDisplayById(lh.level_id) ?? 'Unknown Level'
        }));
    });

    const statusDropdownOptions = $derived(() => {
        return statusState.statuses.map(status => ({
            id: status.id,
            name: status.name,
            disabled: status.id === latestStatusId()
        }));
    });

    const levelDropdownOptions = $derived(() => {
        return levelState.levels.map(level => ({
            id: level.id,
            name: `${level.curriculum.name}: ${level.name}`,
            disabled: level.id === latestLevelId()
        }));
    });
</script>

{#if isLoading || error}
    <LoadingState 
        {isLoading}
        {error}
        loadingText="Loading student information..."
    />
{:else if student}
    <div class="card bg-primary text-primary-content shadow-2xl">
        <div class="card-body p-8">
            <!-- Header Section -->
            <div class="text-center mb-6">
                {#if isEditingName}
                    <div class="flex flex-col items-center space-y-4">
                        <div class="flex flex-col sm:flex-row gap-2 w-full max-w-md">
                            <input 
                                type="text" 
                                bind:value={editingFirstName}
                                placeholder="First Name"
                                class="input input-bordered input-primary bg-base-100 text-base-content flex-1"
                                disabled={isUpdatingName}
                            />
                            <input 
                                type="text" 
                                bind:value={editingLastName}
                                placeholder="Last Name"
                                class="input input-bordered input-primary bg-base-100 text-base-content flex-1"
                                disabled={isUpdatingName}
                            />
                        </div>
                        <div class="flex gap-2">
                            <button 
                                class="btn btn-success btn-sm"
                                disabled={isUpdatingName || !editingFirstName.trim()}
                                onclick={saveNameChanges}
                            >
                                {#if isUpdatingName}
                                    <span class="loading loading-spinner loading-xs"></span>
                                {/if}
                                Save
                            </button>
                            <button 
                                class="btn btn-ghost btn-sm"
                                disabled={isUpdatingName}
                                onclick={cancelEditingName}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                {:else}
                    <div class="flex items-center justify-center gap-3">
                        <a 
                            href="/students/{student.id}" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            class="text-4xl font-bold link link-hover text-primary-content hover:text-primary-content/80 transition-colors"
                        >
                            {getStudentFullName(student)}
                        </a>
                        <button 
                            class="btn btn-ghost btn-sm text-primary-content hover:bg-primary-content/10"
                            onclick={startEditingName}
                            aria-label="Edit student name"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                    </div>
                {/if}
            </div>

            <!-- Main Info Section - Two Columns -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <!-- Left Column -->
                <div class="space-y-4">
                    <!-- Student Since -->
                    <div class="stats shadow-lg bg-base-100 text-base-content w-full">
                        <div class="stat">
                            <div class="stat-figure text-primary">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                            </div>
                            <div class="stat-title">Student Since</div>
                            <div class="stat-value text-lg">
                                <EditableField 
                                    value={student.date_started ? student.date_started.split('T')[0] : ''}
                                    type="date"
                                    displayValue={formatStudentDate(student.date_started)}
                                    isUpdating={isUpdatingStartDate}
                                    onSave={(value) => handleStartDateChange(String(value))}
                                    inputClass="input input-bordered input-sm bg-base-100 text-base-content"
                                    buttonClass="btn btn-ghost btn-sm text-primary hover:bg-primary hover:text-primary-content"
                                />
                            </div>
                        </div>
                    </div>

                    <!-- Current Status and Classes per Week Row -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <StatCard 
                            title="Current Status"
                            value={currentStatusDisplay()}
                            icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                            color="text-accent"
                        />

                        <NumberCounter 
                            value={student.classes_per_week ?? 0}
                            title="Classes per Week"
                            icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>'
                            onChange={handleClassesPerWeekChange}
                            isUpdating={isUpdatingClassesPerWeek}
                            min={0}
                        />
                    </div>

                    <!-- Curriculum and Level Row -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <StatCard 
                            title="Curriculum"
                            value={currentLevelDisplay().split(':')[0] ?? 'Not set'}
                            icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'
                            color="text-accent"
                        />

                        <StatCard 
                            title="Current Level"
                            value={currentLevelDisplay().split(':')[1]?.trim() ?? 'Not set'}
                            icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>'
                            color="text-accent"
                        />
                    </div>

                    <!-- Last Lesson and Next Lesson Row -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <StatCard 
                            title="Last Lesson"
                            value={lastLessonDisplay()}
                            icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                            color="text-info"
                        />

                        <StatCard 
                            title="Next Lesson"
                            value={nextLessonDisplay()}
                            icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                            color="text-success"
                        />
                    </div>
                </div>

                <!-- Right Column - Lessons -->
                <div class="card bg-base-100 text-base-content shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-info">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Lessons
                        </h3>
                        
                        <!-- Lesson Navigation -->
                        <div class="flex justify-between items-center">
                            <button class="btn btn-ghost btn-sm" disabled>
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                                </svg>
                                Previous
                            </button>
                            <span class="text-sm font-medium">Most Recent</span>
                            <button class="btn btn-ghost btn-sm" disabled>
                                Next
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-4 h-4 stroke-current">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                </svg>
                            </button>
                        </div>

                        <!-- Lesson Content -->
                        <div class="overflow-y-auto max-h-85">
                            {#if student.lessons && student.lessons.length > 0}
                                {@const lastLesson = getLastLessonFromStudent(student)}
                                {#if lastLesson}
                                    <!-- Use LessonCard component -->
                                    <LessonCard lessonId={lastLesson.id} />
                                {:else}
                                    <div class="text-center text-base-content/60 py-4">
                                        <p class="font-medium">No past lessons found</p>
                                        <p class="text-sm">This student has no completed lessons</p>
                                    </div>
                                {/if}
                            {:else}
                                <div class="text-center text-base-content/60 py-8">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-12 h-12 stroke-current mb-2">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                    </svg>
                                    <p class="font-medium">No lessons found</p>
                                    <p class="text-sm">This student is not part of any lessons</p>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quiz Results Section -->
            <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20 mb-6">
                <div class="card-body">
                    <h2 class="card-title text-warning">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Quiz Results
                    </h2>
                    <div class="alert alert-info">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span>Quiz functionality will be implemented here. This section is reserved for entering and displaying quiz results.</span>
                    </div>
                </div>
            </div>

            <!-- Notes Section -->
            <div class="divider text-primary-content/70">
                <span class="text-lg font-semibold">Student Notes</span>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor 
                                heading="General Notes" 
                                bind:body={student.notes_general}
                                onSave={saveGeneralNotes}
                            />
                        </div>
                    </div>
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor 
                                heading="Future Plans" 
                                bind:body={student.notes_future}
                                onSave={saveFutureNotes}
                            />
                        </div>
                    </div>
                </div>
                <div class="space-y-4">
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor 
                                heading="Strengths" 
                                bind:body={student.notes_strengths}
                                onSave={saveStrengthsNotes}
                            />
                        </div>
                    </div>
                    <div class="card bg-base-100/10 backdrop-blur-sm border border-primary-content/20">
                        <div class="card-body p-4">
                            <TipexEditor 
                                heading="Areas of Improvement" 
                                bind:body={student.notes_weaknesses}
                                onSave={saveWeaknessesNotes}
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- History Section -->
            <div class="divider text-primary-content/70">
                <span class="text-lg font-semibold">Student History</span>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <HistoryTimeline 
                    title="Status History"
                    icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    historyItems={statusHistoryItems()}
                    dropdownOptions={statusDropdownOptions()}
                    currentItemId={latestStatusId()}
                    isUpdating={isUpdatingStatus}
                    deletingItemId={deletingStatusId}
                    onItemChange={handleStatusChange}
                    onItemDelete={handleDeleteStatusHistory}
                    formatDate={formatStudentDate}
                    emptyStateText="No status history available"
                    emptyStateSubtext="Status changes will appear here"
                />
                
                <HistoryTimeline 
                    title="Level History"
                    icon='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>'
                    historyItems={levelHistoryItems()}
                    dropdownOptions={levelDropdownOptions()}
                    currentItemId={latestLevelId()}
                    isUpdating={isUpdatingLevel}
                    deletingItemId={deletingLevelId}
                    onItemChange={handleLevelChange}
                    onItemDelete={handleDeleteLevelHistory}
                    formatDate={formatStudentDate}
                    emptyStateText="No level history available"
                    emptyStateSubtext="Level changes will appear here"
                />
            </div>
        </div>
    </div>
{/if}