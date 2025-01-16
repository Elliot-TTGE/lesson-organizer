<script lang="ts">
    export const drawerId : string = "sidebar-drawer"
</script>

<div class='drawer drawer-open'>
    <input id={drawerId} type='checkbox' class='drawer-toggle' />
    <div class='drawer-side bg-primary p-4 border-8 border-secondary'>
      <label for={drawerId} aria-label='sidebar'></label>
      <ul class='menu'>
        <li>
          <details class="dropdown dropdown-end w-64 my-16">
            <summary class='btn btn-secondary'>Lesson Calendar</summary>
            <ul class='menu dropdown-content bg-base-200 rounded-box z-[1] w-64 shadow'>
              <li><a href='/'>Week View</a></li>
              <li><a href='/lessons'>Select Week</a></li>
            </ul>
          </details>
        </li>
        <li>
          <details class="dropdown dropdown-end w-64 my-16">
            <summary class='btn btn-secondary'>Students</summary>
            <ul class='menu dropdown-content bg-base-200 rounded-box z-[1] w-64 shadow'>
              <li><a href='/'>Student View</a></li>
              <li><a href='/'>Select Student</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </div>
    <div class='drawer-content'>
      <slot />
    </div>
  </div>