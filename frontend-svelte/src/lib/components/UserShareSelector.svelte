<script lang="ts">
  import type { User, UserLesson } from "../../types/index.d";
  import { fetchUsers } from "../../api/user";
  import { createUserLesson, deleteUserLesson, updateUserLesson, getLessonShares } from "../../api/userLesson";

  // Type for UserShareSelector context - exported for use in parent components
  export interface UserShareSelectorContext {
    userSearchTerm: string;
    filteredUsers: User[];
    showUserDropdown: boolean;
    handleUserSearch: () => void;
    addUser: (user: User, permission?: 'view' | 'edit' | 'manage') => void;
    removeUser: (userId: number) => void;
    updatePermission: (userId: number, permission: 'view' | 'edit' | 'manage') => void;
    isEditing: boolean;
    selectedShares: UserLesson[];
  }

  let { 
    lessonId,
    selectedShares = $bindable([]),
    userSearchTerm = $bindable(""),
    isEditing = false,
    onSharesChange = () => {},
    reset = $bindable(),
    children
  }: { 
    lessonId: number;
    selectedShares: UserLesson[];
    userSearchTerm?: string;
    isEditing?: boolean;
    onSharesChange?: (shares: UserLesson[]) => void;
    reset?: () => void;
    children?: any;
  } = $props();

  // User selection state
  let availableUsers = $state<User[]>([]);
  let filteredUsers = $state<User[]>([]);
  let showUserDropdown = $state(false);
  let userSearchTimeout: number;

  // Set up reset function
  reset = () => {
    showUserDropdown = false;
    userSearchTerm = "";
    if (userSearchTimeout) {
      clearTimeout(userSearchTimeout);
    }
  };

  // Load data when component mounts or when isEditing becomes true
  $effect(() => {
    if (isEditing) {
      loadData();
    }
  });

  // Always load shares for display
  $effect(() => {
    loadShares();
  });

  // Load users and existing shares
  async function loadData() {
    try {
      const usersResponse = await fetchUsers();
      availableUsers = Array.isArray(usersResponse) ? usersResponse : usersResponse.users || [];
      filterUsers();
    } catch (error) {
      console.error("Error loading user data:", error);
    }
  }

  // Load shares (with nested user data from schema)
  async function loadShares() {
    try {
      const sharesResponse = await getLessonShares(lessonId);
      selectedShares = sharesResponse.user_lessons;
      filterUsers();
    } catch (error) {
      console.error("Error loading share data:", error);
    }
  }

  // Filter users based on search term and exclude already shared
  function filterUsers() {
    const search = userSearchTerm.toLowerCase().trim();
    filteredUsers = availableUsers.filter((user: User) => {
      const fullName = `${user.first_name} ${user.last_name}`.toLowerCase();
      const email = user.email.toLowerCase();
      const isAlreadyShared = selectedShares.some((share: UserLesson) => share.user_id === user.id);
      return (fullName.includes(search) || email.includes(search)) && !isAlreadyShared;
    });
  }

  // Handle user search input with debouncing
  function handleUserSearch() {
    if (userSearchTimeout) {
      clearTimeout(userSearchTimeout);
    }
    userSearchTimeout = setTimeout(() => {
      filterUsers();
      showUserDropdown = userSearchTerm.length > 0;
    }, 200);
  }

  // Add user with specified permission (defaults to 'view')
  async function addUser(user: User, permission: 'view' | 'edit' | 'manage' = 'view') {
    try {
      const newShare = await createUserLesson({
        lesson_id: lessonId,
        user_id: user.id,
        permission_level: permission
      });
      
      selectedShares = [...selectedShares, newShare];
      userSearchTerm = "";
      showUserDropdown = false;
      filterUsers();
      onSharesChange(selectedShares);
    } catch (error) {
      console.error("Error sharing lesson:", error);
    }
  }

  // Remove user share
  async function removeUser(userId: number) {
    try {
      const shareToRemove = selectedShares.find(share => share.user_id === userId);
      if (shareToRemove) {
        await deleteUserLesson(shareToRemove.id);
        selectedShares = selectedShares.filter((share: UserLesson) => share.user_id !== userId);
        filterUsers();
        onSharesChange(selectedShares);
      }
    } catch (error) {
      console.error("Error removing share:", error);
    }
  }

  // Update user permission
  async function updatePermission(userId: number, permission: 'view' | 'edit' | 'manage') {
    try {
      const shareToUpdate = selectedShares.find(share => share.user_id === userId);
      if (shareToUpdate) {
        const updatedShare = await updateUserLesson(shareToUpdate.id, {
          permission_level: permission
        });
        
        selectedShares = selectedShares.map(share => 
          share.user_id === userId ? updatedShare : share
        );
        onSharesChange(selectedShares);
      }
    } catch (error) {
      console.error("Error updating permission:", error);
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

  function getPermissionLabel(permission: string): string {
    switch (permission) {
      case 'view': return 'View';
      case 'edit': return 'Edit';
      case 'manage': return 'Manage';
      default: return permission;
    }
  }

  // Expose functions and state to parent via snippet parameters
  const context = $derived({
    userSearchTerm,
    filteredUsers,
    showUserDropdown,
    handleUserSearch,
    addUser,
    removeUser,
    updatePermission,
    isEditing,
    selectedShares
  });
</script>

<!-- Render children with context -->
{@render children?.(context)}