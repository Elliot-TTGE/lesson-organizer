<script lang="ts">
  import type { User, UserLesson } from "../../types/index.d";
  import { createUserLesson, deleteUserLesson, updateUserLesson, getLessonShares } from "../../api/userLesson";
  import { fetchUsers } from "../../api/user";

  interface Props {
    lessonId: number;
    isOpen: boolean;
    onClose: () => void;
  }

  let { lessonId, isOpen, onClose }: Props = $props();

  let users: User[] = $state([]);
  let existingShares: UserLesson[] = $state([]);
  let searchTerm: string = $state("");
  let filteredUsers = $derived(
    users.filter(user => 
      (user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
       user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
       user.email.toLowerCase().includes(searchTerm.toLowerCase())) &&
      !existingShares.some(share => share.user_id === user.id)
    )
  );
  
  let selectedUserId: number | null = $state(null);
  let selectedPermission: 'view' | 'edit' | 'manage' = $state('view');
  let showUserDropdown: boolean = $state(false);
  let isLoading: boolean = $state(false);
  let error: string | null = $state(null);

  // Load data when modal opens
  $effect(() => {
    if (isOpen) {
      loadData();
    }
  });

  async function loadData() {
    isLoading = true;
    error = null;
    try {
      const [usersResponse, sharesResponse] = await Promise.all([
        fetchUsers(),
        getLessonShares(lessonId)
      ]);
      
      // Handle both array and object response formats
      users = Array.isArray(usersResponse) ? usersResponse : usersResponse.users || [];
      existingShares = sharesResponse.user_lessons;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load data';
      console.error('Error loading share data:', err);
    } finally {
      isLoading = false;
    }
  }

  async function handleShareLesson() {
    if (!selectedUserId) return;
    
    isLoading = true;
    error = null;
    try {
      const newShare = await createUserLesson({
        lesson_id: lessonId,
        user_id: selectedUserId,
        permission_level: selectedPermission
      });
      
      existingShares = [...existingShares, newShare];
      selectedUserId = null;
      selectedPermission = 'view';
      searchTerm = "";
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to share lesson';
      console.error('Error sharing lesson:', err);
    } finally {
      isLoading = false;
    }
  }

  async function handleUpdatePermission(shareId: number, newPermission: 'view' | 'edit' | 'manage') {
    isLoading = true;
    error = null;
    try {
      const updatedShare = await updateUserLesson(shareId, {
        permission_level: newPermission
      });
      
      existingShares = existingShares.map(share => 
        share.id === shareId ? updatedShare : share
      );
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to update permission';
      console.error('Error updating permission:', err);
    } finally {
      isLoading = false;
    }
  }

  async function handleRemoveShare(shareId: number) {
    isLoading = true;
    error = null;
    try {
      await deleteUserLesson(shareId);
      existingShares = existingShares.filter(share => share.id !== shareId);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to remove share';
      console.error('Error removing share:', err);
    } finally {
      isLoading = false;
    }
  }

  function selectUser(user: User) {
    selectedUserId = user.id;
    searchTerm = `${user.first_name} ${user.last_name}`;
    showUserDropdown = false;
  }

  function getPermissionLabel(permission: string): string {
    switch (permission) {
      case 'view': return 'Can View';
      case 'edit': return 'Can Edit';
      case 'manage': return 'Can Manage';
      default: return permission;
    }
  }

  function getPermissionColor(permission: string): string {
    switch (permission) {
      case 'view': return 'badge-info';
      case 'edit': return 'badge-warning';
      case 'manage': return 'badge-error';
      default: return 'badge-neutral';
    }
  }
</script>

{#if isOpen}
  <dialog class="modal modal-open" aria-modal="true" aria-labelledby="share-modal-title">
    <div class="modal-box w-11/12 max-w-2xl">
      <h3 id="share-modal-title" class="font-bold text-lg mb-4">Share Lesson</h3>
      
      {#if error}
        <div class="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      {/if}

      {#if isLoading}
        <div class="flex justify-center items-center py-8">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
      {:else}
        <!-- Share with new user section -->
        <div class="mb-6">
          <h4 class="font-semibold mb-3">Share with a user</h4>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- User Search -->
            <div class="md:col-span-2 relative">
              <label class="label" for="user-search">
                <span class="label-text">Search users</span>
              </label>
              <input
                id="user-search"
                type="text"
                placeholder="Search by name or email..."
                bind:value={searchTerm}
                onfocus={() => showUserDropdown = searchTerm.length > 0}
                onblur={() => {
                  setTimeout(() => showUserDropdown = false, 150);
                }}
                oninput={() => {
                  selectedUserId = null;
                  showUserDropdown = searchTerm.length > 0;
                }}
                class="input input-bordered w-full"
              />
              
              {#if showUserDropdown && filteredUsers.length > 0}
                <div class="absolute z-50 w-full mt-1 bg-base-100 border border-base-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  {#each filteredUsers as user (user.id)}
                    <button
                      type="button"
                      class="w-full px-4 py-2 text-left hover:bg-base-200 transition-colors"
                      onclick={() => selectUser(user)}
                    >
                      <div class="font-medium">{user.first_name} {user.last_name}</div>
                      <div class="text-sm text-base-content/70">{user.email}</div>
                    </button>
                  {/each}
                </div>
              {/if}
              
              {#if showUserDropdown && searchTerm.length > 0 && filteredUsers.length === 0}
                <div class="absolute z-50 w-full mt-1 bg-base-100 border border-base-300 rounded-lg shadow-lg">
                  <div class="px-4 py-2 text-sm text-base-content/60">
                    No users found matching "{searchTerm}"
                  </div>
                </div>
              {/if}
            </div>
            
            <!-- Permission Level -->
            <div>
              <label class="label" for="permission-select">
                <span class="label-text">Permission</span>
              </label>
              <select
                id="permission-select"
                bind:value={selectedPermission}
                class="select select-bordered w-full"
              >
                <option value="view">Can View</option>
                <option value="edit">Can Edit</option>
                <option value="manage">Can Manage</option>
              </select>
            </div>
          </div>
          
          <div class="mt-4">
            <button
              onclick={handleShareLesson}
              disabled={!selectedUserId || isLoading}
              class="btn btn-primary"
            >
              {isLoading ? 'Sharing...' : 'Share Lesson'}
            </button>
          </div>
        </div>

        <!-- Existing shares section -->
        <div class="divider"></div>
        
        <div>
          <h4 class="font-semibold mb-3">Current shares ({existingShares.length})</h4>
          
          {#if existingShares.length === 0}
            <div class="text-base-content/60 italic py-4">
              This lesson is not shared with anyone yet.
            </div>
          {:else}
            <div class="space-y-3">
              {#each existingShares as share (share.id)}
                <div class="flex items-center justify-between p-3 bg-base-200 rounded-lg">
                  <div class="flex-1">
                    <div class="font-medium">
                      {share.user?.first_name} {share.user?.last_name}
                    </div>
                    <div class="text-sm text-base-content/70">
                      {share.user?.email}
                    </div>
                    {#if share.shared_at}
                      <div class="text-xs text-base-content/50">
                        Shared on {new Date(share.shared_at).toLocaleDateString()}
                      </div>
                    {/if}
                  </div>
                  
                  <div class="flex items-center gap-2">
                    <!-- Permission Badge/Selector -->
                    <div class="dropdown dropdown-end">
                      <button
                        tabindex="0"
                        class="badge {getPermissionColor(share.permission_level)} cursor-pointer"
                      >
                        {getPermissionLabel(share.permission_level)}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <ul class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-36">
                        <li>
                          <button onclick={() => handleUpdatePermission(share.id, 'view')}>
                            <span class="badge badge-info badge-sm">Can View</span>
                          </button>
                        </li>
                        <li>
                          <button onclick={() => handleUpdatePermission(share.id, 'edit')}>
                            <span class="badge badge-warning badge-sm">Can Edit</span>
                          </button>
                        </li>
                        <li>
                          <button onclick={() => handleUpdatePermission(share.id, 'manage')}>
                            <span class="badge badge-error badge-sm">Can Manage</span>
                          </button>
                        </li>
                      </ul>
                    </div>
                    
                    <!-- Remove Share Button -->
                    <button
                      onclick={() => handleRemoveShare(share.id)}
                      class="btn btn-ghost btn-xs text-error hover:bg-error hover:text-error-content"
                      title="Remove share"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
      
      <!-- Modal Actions -->
      <div class="modal-action">
        <button onclick={onClose} class="btn">Close</button>
      </div>
    </div>
  </dialog>
{/if}