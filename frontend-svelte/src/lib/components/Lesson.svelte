<script lang="ts">
    interface Props {
        weekday: string,
        date: string,
        time: string,
        plan: string
    }

    let {weekday, date, time, plan} : Props = $props()
</script>

<style>
    p {
        color: darkorchid
    }
</style>

<div class='bg-neutral m-1 w-64 rounded'>
    <p>{weekday}</p>
    <p>{date}:</p>
    <p>{time}:</p>
    <p>Today's plan:</p>
    <p>{plan}</p>

    <div class='bg-accent'>
        <p>Card Concepts Taught</p>
    </div>
    <div class='bg-accent'>
        <p>Card Lesson Notes</p>
    </div>
    <div class='bg-base-300'></div>
</div>