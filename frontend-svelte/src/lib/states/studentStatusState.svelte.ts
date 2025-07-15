import type { StudentStatus } from "../../types";
import { fetchStudentStatuses } from "../../api/studentStatus";

interface StatusState {
  statuses: StudentStatus[];
  isLoading: boolean;
  error: string | null;
}

export const statusState = $state<StatusState>({
  statuses: [],
  isLoading: false,
  error: null
});

/**
 * Fetches all student statuses and updates the state
 */
export async function refreshStatuses(): Promise<void> {
  statusState.isLoading = true;
  statusState.error = null;
  
  try {
    statusState.statuses = await fetchStudentStatuses();
  } catch (err) {
    statusState.error = err instanceof Error ? err.message : 'Failed to fetch statuses';
    console.error('Error fetching statuses:', err);
  } finally {
    statusState.isLoading = false;
  }
}

/**
 * Gets a status by ID from the current state
 * @param id - The status ID to find
 * @returns The status object or undefined if not found
 */
export function getStatusById(id: number): StudentStatus | undefined {
  return statusState.statuses.find(status => status.id === id);
}

/**
 * Gets a status name by ID from the current state
 * @param id - The status ID to find
 * @returns The status name or undefined if not found
 */
export function getStatusNameById(id: number): string | undefined {
  return getStatusById(id)?.name;
}