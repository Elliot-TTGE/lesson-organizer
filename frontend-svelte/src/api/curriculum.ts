import type { Curriculum } from "../types";
import { apiRequest } from "./apiClient";
import type { QueryParams } from "./apiClient";

export async function fetchCurriculums(params: QueryParams = {}): Promise<Curriculum[]> {
    return await apiRequest<Curriculum[]>('/curriculums', 'GET', null, {}, params);
}