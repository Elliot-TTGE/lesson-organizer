export interface Student {
    id: number;
    name: string;
}

export interface Lesson {
    id: number;
    datetime: string;
    plan: string;
    concepts_taught: string;
    additional_notes: string;
    students: Student[];
}