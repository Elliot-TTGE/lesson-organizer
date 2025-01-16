<script lang='ts'>
  import Drawer from '$lib/components/Drawer.svelte'
  import Lesson from '$lib/components/Lesson.svelte'
</script>

<Drawer drawerId='sidebar-drawer'>
  <div class='navbar bg shadow'>
    <div class='flex bg-base-300 ring-accent py-4 px-16 m-1 rounded-box shadow justify-between'>
      <div>Week Of: </div>
      <div class="ml-4">01/13/24</div>
    </div>
  </div>
  <label for='sidebar-drawer' class='drawer-overlay'></label>

  <div class='flex flex-row space-x-4'>
    <Lesson 
      weekday="Monday"
      date="01/13/25"
      time='1:00 PM'
      plan='plan'

    />
    <Lesson 
      weekday="Tuesday"
      date="01/14/25"
      time='1:00 PM'
      plan='plan'
    />
  </div>
</Drawer>