<script lang="ts">
  interface Props {
    weekday: string;
    date: string;
    time: string;
    student: string;
    plan: string;
    concepts: string;
    notes: string;
  }

  let { weekday, date, time, student, plan, concepts, notes }: Props = $props();
</script>

<div class="m-4 w-64 rounded bg-neutral">
  <div class="flex flex-col space-y-2 p-2">
    <p>{weekday}</p>
    <p>{date}:</p>
    <p>{time}:</p>
    <p>{student}</p>
    <div>
      <p>Today's plan:</p>
      <p class="min-h-24">
        {plan}
      </p>
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p>Card Concepts Taught</p>
      <p>{concepts}</p>
    </div>
    <div class="mx-2 min-h-32 bg-accent">
      <p>Card Lesson Notes</p>
      <p>{notes}</p>
    </div>
  </div>
</div>

<style>
  p {
    color: darkorchid;
  }
</style>
