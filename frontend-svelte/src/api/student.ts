import type { Student } from "../types";
import type { QueryParams } from "./apiClient";
import { apiRequest } from "./apiClient";

export async function fetchStudents(params: QueryParams = {}): Promise<Student[]> {
    return await apiRequest<Student[]>('/students', 'GET', null, {}, params);
}

export async function createStudent(student: Student): Promise<Student> {
    return await apiRequest<Student>('/students', 'POST', student);
}