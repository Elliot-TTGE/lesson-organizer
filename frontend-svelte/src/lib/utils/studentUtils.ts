import type { Student, StudentLevelHistory, StudentStatusHistory, Lesson } from '../../types';

/**
 * Gets the latest level ID from a student's level history
 * @param student - The student object containing level_history
 * @returns The level_id of the most recent level history entry, or null if none exists
 */
export function getLatestLevelId(student: Student): number | null {
    if (!student.level_history || student.level_history.length === 0) {
        return null;
    }
    
    // Sort by start_date descending to get the most recent entry
    const sortedHistory = [...student.level_history].sort((a, b) => 
        new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
    );
    
    return sortedHistory[0].level_id;
}

/**
 * Gets the latest level history entry from a student
 * @param student - The student object containing level_history
 * @returns The most recent StudentLevelHistory entry, or null if none exists
 */
export function getLatestLevelHistory(student: Student): StudentLevelHistory | null {
    if (!student.level_history || student.level_history.length === 0) {
        return null;
    }
    
    // Sort by start_date descending to get the most recent entry
    const sortedHistory = [...student.level_history].sort((a, b) => 
        new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
    );
    
    return sortedHistory[0];
}

/**
 * Gets the latest status ID from a student's status history
 * @param student - The student object containing status_history
 * @returns The status_id of the most recent status history entry, or null if none exists
 */
export function getLatestStatusId(student: Student): number | null {
    if (!student.status_history || student.status_history.length === 0) {
        return null;
    }
    
    // Sort by changed_at descending to get the most recent entry
    const sortedHistory = [...student.status_history].sort((a, b) => 
        new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime()
    );
    
    return sortedHistory[0].status_id;
}

/**
 * Gets the latest status history entry from a student
 * @param student - The student object containing status_history
 * @returns The most recent StudentStatusHistory entry, or null if none exists
 */
export function getLatestStatusHistory(student: Student): StudentStatusHistory | null {
    if (!student.status_history || student.status_history.length === 0) {
        return null;
    }
    
    // Sort by changed_at descending to get the most recent entry
    const sortedHistory = [...student.status_history].sort((a, b) => 
        new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime()
    );
    
    return sortedHistory[0];
}

/**
 * Gets the student's full name
 * @param student - The student object
 * @returns The formatted full name
 */
export function getStudentFullName(student: Student): string {
    return `${student.first_name} ${student.last_name || ''}`.trim();
}

/**
 * Formats a date string for display
 * @param dateString - ISO date string
 * @returns Formatted date string or 'Not set' if null/undefined
 */
export function formatStudentDate(dateString?: string): string {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
}

/**
 * Formats a lesson date and time for display
 * @param lesson - The lesson object with datetime
 * @returns Formatted date and time string
 */
export function formatLessonDateTime(lesson: Lesson): string {
    const lessonDate = new Date(lesson.datetime);
    
    return lessonDate.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
    }) + ' ' + lessonDate.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

/**
 * Gets the most recent past lesson from a student's lessons
 * @param student - The student object containing lessons
 * @returns The most recent past lesson, or null if none exists
 */
export function getLastLessonFromStudent(student: Student): Lesson | null {
    if (!student.lessons || student.lessons.length === 0) {
        return null;
    }

    const now = new Date();
    
    // Filter lessons to only include those in the past, then sort by datetime descending
    const pastLessons = student.lessons
        .filter(lesson => new Date(lesson.datetime) < now)
        .sort((a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime());
    
    return pastLessons.length > 0 ? pastLessons[0] : null;
}

/**
 * Gets the next upcoming lesson from a student's lessons
 * @param student - The student object containing lessons
 * @returns The next upcoming lesson, or null if none exists
 */
export function getNextLessonFromStudent(student: Student): Lesson | null {
    if (!student.lessons || student.lessons.length === 0) {
        return null;
    }

    const now = new Date();
    
    // Filter lessons to only include those in the future, then sort by datetime ascending
    const futureLessons = student.lessons
        .filter(lesson => new Date(lesson.datetime) > now)
        .sort((a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime());
    
    return futureLessons.length > 0 ? futureLessons[0] : null;
}

/**
 * Gets all lessons from a student sorted chronologically (newest first)
 * @param student - The student object containing lessons
 * @returns Array of lessons sorted by datetime descending
 */
export function getSortedLessonsFromStudent(student: Student): Lesson[] {
    if (!student.lessons || student.lessons.length === 0) {
        return [];
    }
    
    // Sort by datetime descending (newest first)
    return [...student.lessons].sort((a, b) => 
        new Date(b.datetime).getTime() - new Date(a.datetime).getTime()
    );
}

/**
 * Gets all past lessons from a student sorted chronologically (newest first)
 * @param student - The student object containing lessons
 * @returns Array of past lessons sorted by datetime descending
 */
export function getPastLessonsFromStudent(student: Student): Lesson[] {
    if (!student.lessons || student.lessons.length === 0) {
        return [];
    }

    const now = new Date();
    
    // Filter lessons to only include those in the past, then sort by datetime descending
    return student.lessons
        .filter(lesson => new Date(lesson.datetime) < now)
        .sort((a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime());
}
