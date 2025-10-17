import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { isAuthenticated, isAdmin } from '$lib/utils/auth';

export const load: PageLoad = async () => {
    try {
        // Check if user is authenticated
        if (!(await isAuthenticated())) {
            throw redirect(302, '/login');
        }
        
        // Check if user is admin
        if (!(await isAdmin())) {
            throw redirect(302, '/lessons');
        }
        
        return {};
    } catch (error) {
        // If it's already a redirect, re-throw it
        if (error && typeof error === 'object' && 'status' in error) {
            throw error;
        }
        // Otherwise redirect to login
        throw redirect(302, '/login');
    }
};