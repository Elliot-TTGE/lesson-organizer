import type { Curriculum } from "../../types";
import { fetchCurriculums } from "../../api/curriculum";

interface CurriculumState {
  curriculums: Curriculum[];
  isLoading: boolean;
  error: string | null;
}

export const curriculumState = $state<CurriculumState>({
  curriculums: [],
  isLoading: false,
  error: null
});

/**
 * Fetches all curriculums and updates the state
 */
export async function refreshCurriculums(): Promise<void> {
  curriculumState.isLoading = true;
  curriculumState.error = null;
  
  try {
    curriculumState.curriculums = await fetchCurriculums();
  } catch (err) {
    curriculumState.error = err instanceof Error ? err.message : 'Failed to fetch curriculums';
    console.error('Error fetching curriculums:', err);
  } finally {
    curriculumState.isLoading = false;
  }
}

/**
 * Gets a curriculum by ID from the current state
 * @param id - The curriculum ID to find
 * @returns The curriculum object or undefined if not found
 */
export function getCurriculumById(id: number): Curriculum | undefined {
  return curriculumState.curriculums.find(curriculum => curriculum.id === id);
}

/**
 * Gets a curriculum name by ID from the current state
 * @param id - The curriculum ID to find
 * @returns The curriculum name or undefined if not found
 */
export function getCurriculumNameById(id: number): string | undefined {
  return getCurriculumById(id)?.name;
}