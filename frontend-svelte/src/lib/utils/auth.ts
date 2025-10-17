import { browser } from '$app/environment';
import { fetchCurrentUser as fetchCurrentUserAPI } from '../../api/user';
import type { User } from '../../types';

/**
 * Authentication utility functions
 * These functions provide direct backend verification for auth state
 */

/**
 * Get the current authenticated user
 * @returns User object if authenticated, null otherwise
 */
export async function getCurrentUser(): Promise<User | null> {
    if (!browser) return null;
    
    try {
        return await fetchCurrentUserAPI();
    } catch (error) {
        console.error('Failed to fetch current user:', error);
        return null;
    }
}

/**
 * Check if user is authenticated
 * @returns True if user is authenticated, false otherwise
 */
export async function isAuthenticated(): Promise<boolean> {
    try {
        await fetchCurrentUserAPI();
        return true;
    } catch {
        return false;
    }
}

/**
 * Check if current user has admin privileges
 * @returns True if user is admin, false otherwise
 */
export async function isAdmin(): Promise<boolean> {
    try {
        const user = await fetchCurrentUserAPI();
        return user?.role === 'admin' || false;
    } catch {
        return false;
    }
}

/**
 * Log out the current user
 * Clears authentication and redirects to login page
 */
export function logout(): void {
    // Clear any authentication cookies or tokens if needed
    if (browser) {
        // Redirect to login page
        window.location.href = '/login';
    }
}