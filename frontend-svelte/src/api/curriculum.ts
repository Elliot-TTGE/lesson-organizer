import type { Curriculum } from "../types";
import { apiRequest } from "./apiClient";
import type { QueryParams } from "./apiClient";

// Define the allowed fields that can be modified
export type CurriculumCreateFields = Required<Pick<Curriculum, 'name'>>;
export type CurriculumUpdateFields = Pick<Curriculum, 'name'>;

function extractCurriculumFields(curriculum: Curriculum): CurriculumUpdateFields {
    const { name } = curriculum;
    return { name };
}

export async function fetchCurriculums(params: QueryParams = {}): Promise<Curriculum[]> {
    return await apiRequest<Curriculum[]>('/curriculums', 'GET', null, {}, params);
}

export async function fetchCurriculum(id: number): Promise<Curriculum> {
    return await apiRequest<Curriculum>(`/curriculums/${id}`, 'GET');
}

export async function createCurriculum(curriculum: CurriculumCreateFields): Promise<Curriculum> {
    const payload = {
        curriculum
    };
    return await apiRequest<Curriculum>('/curriculums', 'POST', payload);
}

export async function updateCurriculum(id: number, curriculum: Partial<CurriculumUpdateFields> | Curriculum): Promise<Curriculum> {
    const curriculumData = 'id' in curriculum ? extractCurriculumFields(curriculum) : curriculum;
    
    const payload = {
        curriculum: curriculumData
    };
    return await apiRequest<Curriculum>(`/curriculums/${id}`, 'PUT', payload);
}

export async function deleteCurriculum(id: number): Promise<void> {
    await apiRequest<void>(`/curriculums/${id}`, 'DELETE');
}