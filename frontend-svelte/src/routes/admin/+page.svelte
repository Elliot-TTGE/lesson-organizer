<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { 
        fetchUsers, 
        fetchUserStats,
        createUser,
        updateUser,
        deleteUser
    } from '../../api/user';
    import type { UsersResponse, UserStatsResponse, UserSearchParams } from '../../api/user';
    import type { User } from '../../types';
    import { getCurrentUser } from '$lib/utils/auth';
    
    let users: User[] = $state([]);
    let stats: UserStatsResponse | null = $state(null);
    let loading = $state(true);
    let error = $state('');
    let currentUser: User | null = $state(null);
    
    // Search and filter state
    let searchTerm = $state('');
    let selectedRole = $state('');
    let currentPage = $state(1);
    let pagination = $state<UsersResponse['pagination'] | null>(null);
    
    // Debounce search input
    let searchTimeout: number;
    
    // Form state
    let showCreateForm = $state(false);
    let showEditForm = $state(false);
    let editingUser: User | null = $state(null);
    let formData = $state({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        role: 'instructor' as 'admin' | 'assistant' | 'instructor'
    });
    
    const roleOptions = [
        { value: '', label: 'All Roles' },
        { value: 'admin', label: 'Admin' },
        { value: 'assistant', label: 'Assistant' }, 
        { value: 'instructor', label: 'Instructor' }
    ];

    async function loadUsers() {
        try {
            loading = true;
            const params: UserSearchParams = {
                page: currentPage,
                per_page: 20
            };
            
            if (searchTerm) params.search = searchTerm;
            if (selectedRole) params.role = selectedRole;
            
            const response = await fetchUsers(params);
            
            // Handle both array and paginated responses
            if (Array.isArray(response)) {
                users = response;
                pagination = null;
            } else {
                users = response.users || [];
                pagination = response.pagination || null;
            }
        } catch (err) {
            error = 'Failed to load users';
            console.error('Error loading users:', err);
        } finally {
            loading = false;
        }
    }

    async function loadStats() {
        try {
            stats = await fetchUserStats();
        } catch (err) {
            console.error('Error loading stats:', err);
        }
    }

    async function handleSearch() {
        currentPage = 1;
        await loadUsers();
    }

    async function handleCreateUser() {
        try {
            await createUser(formData);
            showCreateForm = false;
            resetForm();
            await loadUsers();
            await loadStats();
        } catch (err) {
            error = 'Failed to create user';
            console.error('Error creating user:', err);
        }
    }

    async function handleEditUser() {
        if (!editingUser) return;
        
        try {
            const updateData: any = {
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                role: formData.role
            };
            
            if (formData.password) {
                updateData.password = formData.password;
            }
            
            await updateUser(editingUser.id, updateData);
            showEditForm = false;
            editingUser = null;
            resetForm();
            await loadUsers();
        } catch (err) {
            error = 'Failed to update user';
            console.error('Error updating user:', err);
        }
    }

    async function handleDeleteUser(user: User) {
        if (!confirm(`Are you sure you want to delete ${user.first_name} ${user.last_name}?`)) {
            return;
        }
        
        try {
            await deleteUser(user.id);
            await loadUsers();
            await loadStats();
        } catch (err) {
            error = 'Failed to delete user';
            console.error('Error deleting user:', err);
        }
    }

    function startEdit(user: User) {
        editingUser = user;
        formData = {
            first_name: user.first_name,
            last_name: user.last_name,
            email: user.email,
            password: '',
            role: user.role as 'admin' | 'assistant' | 'instructor'
        };
        showEditForm = true;
    }

    function resetForm() {
        formData = {
            first_name: '',
            last_name: '',
            email: '',
            password: '',
            role: 'instructor'
        };
    }

    function getRoleBadgeClass(role: string) {
        switch (role) {
            case 'admin': return 'badge-error';
            case 'assistant': return 'badge-warning';
            case 'instructor': return 'badge-success';
            default: return 'badge-neutral';
        }
    }

    onMount(() => {
        loadUsers();
        loadStats();
        loadCurrentUser();
    });

    onDestroy(() => {
        clearTimeout(searchTimeout);
    });

    async function loadCurrentUser() {
        currentUser = await getCurrentUser();
    }

    function handleSearchInput(event: Event) {
        const target = event.target as HTMLInputElement;
        searchTerm = target.value;
        
        // Clear existing timeout
        clearTimeout(searchTimeout);
        
        // Set new timeout for debounced search
        searchTimeout = setTimeout(() => {
            handleSearch();
        }, 300);
    }

    function handleRoleChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        selectedRole = target.value;
        handleSearch();
    }
</script>

<svelte:head>
    <title>Admin Panel - User Management</title>
</svelte:head>

<div class="container mx-auto p-6 pt-20">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Admin Panel</h1>
        {#if currentUser}
            <div class="text-sm text-base-content/70">
                Welcome, {currentUser.first_name} {currentUser.last_name}
            </div>
        {/if}
    </div>

    {#if error}
        <div class="alert alert-error mb-6">
            <span>{error}</span>
            <button class="btn btn-sm btn-ghost" onclick={() => error = ''}>×</button>
        </div>
    {/if}

    <!-- Stats Cards -->
    {#if stats}
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="stat bg-base-200 rounded-lg">
                <div class="stat-title">Total Users</div>
                <div class="stat-value text-primary">{stats.users.total}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
                <div class="stat-title">Admins</div>
                <div class="stat-value text-error">{stats.users.admins}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
                <div class="stat-title">Assistants</div>
                <div class="stat-value text-warning">{stats.users.assistants}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
                <div class="stat-title">Instructors</div>
                <div class="stat-value text-success">{stats.users.instructors}</div>
            </div>
        </div>
    {/if}

    <!-- Search and Filters -->
    <div class="card bg-base-100 shadow-lg mb-6">
        <div class="card-body">
            <div class="flex flex-col lg:flex-row gap-4 items-end">
                <div class="form-control flex-1">
                    <label class="label" for="search">
                        <span class="label-text">Search Users</span>
                    </label>
                    <input
                        id="search"
                        type="text"
                        placeholder="Search by name or email..."
                        class="input input-bordered"
                        value={searchTerm}
                        oninput={handleSearchInput}
                    />
                </div>
                
                <div class="form-control">
                    <label class="label" for="role-filter">
                        <span class="label-text">Filter by Role</span>
                    </label>
                    <select id="role-filter" class="select select-bordered" value={selectedRole} onchange={handleRoleChange}>
                        {#each roleOptions as option}
                            <option value={option.value}>{option.label}</option>
                        {/each}
                    </select>
                </div>
                
                <button class="btn btn-primary" onclick={() => showCreateForm = true}>
                    <span class="text-lg">+</span>
                    Add User
                </button>
            </div>
        </div>
    </div>

    <!-- Users Table -->
    <div class="card bg-base-100 shadow-lg">
        <div class="card-body">
            {#if loading}
                <div class="flex justify-center p-8">
                    <span class="loading loading-spinner loading-lg"></span>
                </div>
            {:else if users.length === 0}
                <div class="text-center p-8 text-base-content/70">
                    No users found matching your criteria.
                </div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="table table-zebra">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Created</th>
                                <th>Last Login</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each users as user}
                                <tr>
                                    <td>
                                        <span class="font-mono text-sm text-base-content/60">
                                            #{user.id}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="font-semibold">
                                            {user.first_name} {user.last_name}
                                        </div>
                                    </td>
                                    <td>{user.email}</td>
                                    <td>
                                        <span class="badge {getRoleBadgeClass(user.role)}">
                                            {user.role}
                                        </span>
                                    </td>
                                    <td>
                                        {new Date(user.created_date).toLocaleDateString()}
                                    </td>
                                    <td>
                                        {user.last_login 
                                            ? new Date(user.last_login).toLocaleDateString() 
                                            : 'Never'
                                        }
                                    </td>
                                    <td>
                                        <div class="flex gap-2">
                                            <button 
                                                class="btn btn-sm btn-primary"
                                                onclick={() => startEdit(user)}
                                            >
                                                Edit
                                            </button>
                                            <button 
                                                class="btn btn-sm btn-error"
                                                onclick={() => handleDeleteUser(user)}
                                                disabled={user.id === currentUser?.id}
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                <!-- Pagination Info -->
                {#if pagination}
                    <div class="flex justify-between items-center mt-4 text-sm text-base-content/60">
                        <span>
                            Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} users
                        </span>
                        <span>
                            Page {pagination.page} of {pagination.pages} ({pagination.per_page} per page)
                        </span>
                    </div>
                {/if}

                <!-- Pagination -->
                {#if pagination && pagination.pages > 1}
                    <div class="flex justify-center mt-6">
                        <div class="join">
                            <button 
                                class="join-item btn"
                                disabled={currentPage <= 1}
                                onclick={() => { currentPage = currentPage - 1; loadUsers(); }}
                            >
                                «
                            </button>
                            
                            {#each Array(pagination.pages) as _, i}
                                <button 
                                    class="join-item btn {currentPage === i + 1 ? 'btn-active' : ''}"
                                    onclick={() => { currentPage = i + 1; loadUsers(); }}
                                >
                                    {i + 1}
                                </button>
                            {/each}
                            
                            <button 
                                class="join-item btn"
                                disabled={currentPage >= pagination.pages}
                                onclick={() => { currentPage = currentPage + 1; loadUsers(); }}
                            >
                                »
                            </button>
                        </div>
                    </div>
                {/if}
            {/if}
        </div>
    </div>
</div>

<!-- Create User Modal -->
{#if showCreateForm}
    <div class="modal modal-open">
        <div class="modal-box w-11/12 max-w-2xl">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-xl font-bold text-base-content">
                    <span class="inline-flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Create New User
                    </span>
                </h3>
                <button 
                    type="button" 
                    class="btn btn-sm btn-circle btn-ghost" 
                    onclick={() => { showCreateForm = false; resetForm(); }}
                    aria-label="Close modal"
                >
                    ✕
                </button>
            </div>
            
            <form onsubmit={(e) => { e.preventDefault(); handleCreateUser(); }} class="space-y-6">
                <!-- Personal Information Section -->
                <div class="bg-base-200 rounded-lg p-4">
                    <h4 class="text-sm font-medium text-base-content/70 mb-4 uppercase tracking-wide">Personal Information</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label" for="create-first-name">
                                <span class="label-text font-medium">First Name *</span>
                            </label>
                            <input
                                id="create-first-name"
                                type="text"
                                class="input input-bordered focus:input-primary"
                                bind:value={formData.first_name}
                                placeholder="Enter first name"
                                required
                            />
                        </div>
                        
                        <div class="form-control">
                            <label class="label" for="create-last-name">
                                <span class="label-text font-medium">Last Name *</span>
                            </label>
                            <input
                                id="create-last-name"
                                type="text"
                                class="input input-bordered focus:input-primary"
                                bind:value={formData.last_name}
                                placeholder="Enter last name"
                                required
                            />
                        </div>
                    </div>
                    
                    <div class="form-control mt-4">
                        <label class="label" for="create-email">
                            <span class="label-text font-medium">Email Address *</span>
                        </label>
                        <input
                            id="create-email"
                            type="email"
                            class="input input-bordered focus:input-primary"
                            bind:value={formData.email}
                            placeholder="user@example.com"
                            required
                        />
                    </div>
                </div>

                <!-- Account Information Section -->
                <div class="bg-base-200 rounded-lg p-4">
                    <h4 class="text-sm font-medium text-base-content/70 mb-4 uppercase tracking-wide">Account Information</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label" for="create-password">
                                <span class="label-text font-medium">Password *</span>
                            </label>
                            <input
                                id="create-password"
                                type="password"
                                class="input input-bordered focus:input-primary"
                                bind:value={formData.password}
                                placeholder="Enter secure password"
                                required
                            />
                        </div>
                        
                        <div class="form-control">
                            <label class="label" for="create-role">
                                <span class="label-text font-medium">Role *</span>
                            </label>
                            <select id="create-role" class="select select-bordered focus:select-primary" bind:value={formData.role}>
                                <option value="instructor">Instructor</option>
                                <option value="assistant">Assistant</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Modal Actions -->
                <div class="flex justify-end gap-3 pt-4 border-t border-base-300">
                    <button type="button" class="btn btn-ghost" onclick={() => { showCreateForm = false; resetForm(); }}>
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-primary gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Create User
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

<!-- Edit User Modal -->
{#if showEditForm && editingUser}
    <div class="modal modal-open">
        <div class="modal-box w-11/12 max-w-2xl">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-xl font-bold text-base-content">
                    <span class="inline-flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Edit User
                    </span>
                </h3>
                <button 
                    type="button" 
                    class="btn btn-sm btn-circle btn-ghost" 
                    onclick={() => { showEditForm = false; editingUser = null; resetForm(); }}
                    aria-label="Close modal"
                >
                    ✕
                </button>
            </div>
            
            <form onsubmit={(e) => { e.preventDefault(); handleEditUser(); }} class="space-y-6">
                <!-- Personal Information Section -->
                <div class="bg-base-200 rounded-lg p-4">
                    <h4 class="text-sm font-medium text-base-content/70 mb-4 uppercase tracking-wide">Personal Information</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label" for="edit-first-name">
                                <span class="label-text font-medium">First Name *</span>
                            </label>
                            <input
                                id="edit-first-name"
                                type="text"
                                class="input input-bordered focus:input-secondary"
                                bind:value={formData.first_name}
                                placeholder="Enter first name"
                                required
                            />
                        </div>
                        
                        <div class="form-control">
                            <label class="label" for="edit-last-name">
                                <span class="label-text font-medium">Last Name *</span>
                            </label>
                            <input
                                id="edit-last-name"
                                type="text"
                                class="input input-bordered focus:input-secondary"
                                bind:value={formData.last_name}
                                placeholder="Enter last name"
                                required
                            />
                        </div>
                    </div>
                    
                    <div class="form-control mt-4">
                        <label class="label" for="edit-email">
                            <span class="label-text font-medium">Email Address *</span>
                        </label>
                        <input
                            id="edit-email"
                            type="email"
                            class="input input-bordered focus:input-secondary"
                            bind:value={formData.email}
                            placeholder="user@example.com"
                            required
                        />
                    </div>
                </div>

                <!-- Account Information Section -->
                <div class="bg-base-200 rounded-lg p-4">
                    <h4 class="text-sm font-medium text-base-content/70 mb-4 uppercase tracking-wide">Account Information</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label" for="edit-password">
                                <span class="label-text font-medium">Password</span>
                                <span class="label-text-alt text-base-content/50">Optional</span>
                            </label>
                            <input
                                id="edit-password"
                                type="password"
                                class="input input-bordered focus:input-secondary"
                                bind:value={formData.password}
                                placeholder="Leave blank to keep current password"
                            />
                        </div>
                        
                        <div class="form-control">
                            <label class="label" for="edit-role">
                                <span class="label-text font-medium">Role *</span>
                                {#if editingUser.id === currentUser?.id}
                                    <span class="label-text-alt text-warning">Cannot change own role</span>
                                {/if}
                            </label>
                            <select 
                                id="edit-role" 
                                class="select select-bordered focus:select-secondary" 
                                bind:value={formData.role}
                                disabled={editingUser.id === currentUser?.id}
                            >
                                <option value="instructor">Instructor</option>
                                <option value="assistant">Assistant</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Modal Actions -->
                <div class="flex justify-end gap-3 pt-4 border-t border-base-300">
                    <button type="button" class="btn btn-ghost" onclick={() => { showEditForm = false; editingUser = null; resetForm(); }}>
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-secondary gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        Update User
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}