<script lang="ts">
  import type { Student } from "../../types";
  import { fetchStudents } from "../../api/student";

  // Type for StudentSelector context - exported for use in parent components
  export interface StudentSelectorContext {
    studentSearchTerm: string;
    filteredStudents: Student[];
    showStudentDropdown: boolean;
    handleStudentSearch: () => void;
    addStudent: (student: Student) => void;
    removeStudent: (studentId: number) => void;
    isEditing: boolean;
    selectedStudents: Student[];
  }

  let { 
    selectedStudents = $bindable(),
    studentSearchTerm = $bindable(""),
    isEditing = false,
    onStudentsChange = () => {},
    reset = $bindable(),
    children
  }: { 
    selectedStudents: Student[];
    studentSearchTerm?: string;
    isEditing?: boolean;
    onStudentsChange?: (students: Student[]) => void;
    reset?: () => void;
    children?: any;
  } = $props();

  // Student selection state - exposed via context or direct access
  let availableStudents = $state<Student[]>([]);
  let filteredStudents = $state<Student[]>([]);
  let showStudentDropdown = $state(false);
  let studentSearchTimeout: number;

  // Set up reset function
  reset = () => {
    showStudentDropdown = false;
    studentSearchTerm = "";
    if (studentSearchTimeout) {
      clearTimeout(studentSearchTimeout);
    }
  };

  // Load students when component mounts or when isEditing becomes true
  $effect(() => {
    if (isEditing) {
      loadStudents();
    }
  });

  // Load students from API
  async function loadStudents() {
    try {
      const response = await fetchStudents();
      availableStudents = response.students;
      filterStudents();
    } catch (error) {
      console.error("Error loading students:", error);
    }
  }

  // Filter students based on search term and exclude already selected
  function filterStudents() {
    const search = studentSearchTerm.toLowerCase().trim();
    filteredStudents = availableStudents.filter((student: Student) => {
      const fullName = `${student.first_name} ${student.last_name || ''}`.toLowerCase();
      const isAlreadySelected = selectedStudents.some((s: Student) => s.id === student.id);
      return fullName.includes(search) && !isAlreadySelected;
    });
  }

  // Handle student search input with debouncing
  function handleStudentSearch() {
    if (studentSearchTimeout) {
      clearTimeout(studentSearchTimeout);
    }
    studentSearchTimeout = setTimeout(() => {
      filterStudents();
      showStudentDropdown = studentSearchTerm.length > 0;
    }, 200);
  }

  // Add student to selected list
  function addStudent(student: Student) {
    selectedStudents = [...selectedStudents, student];
    studentSearchTerm = "";
    showStudentDropdown = false;
    filterStudents();
    onStudentsChange(selectedStudents);
  }

  // Remove student from selected list
  function removeStudent(studentId: number) {
    selectedStudents = selectedStudents.filter((s: Student) => s.id !== studentId);
    filterStudents();
    onStudentsChange(selectedStudents);
  }

  // Expose functions and state to parent via snippet parameters
  const context = $derived({
    studentSearchTerm,
    filteredStudents,
    showStudentDropdown,
    handleStudentSearch,
    addStudent,
    removeStudent,
    isEditing,
    selectedStudents
  });
</script>

<!-- Render children with context -->
{@render children?.(context)}
