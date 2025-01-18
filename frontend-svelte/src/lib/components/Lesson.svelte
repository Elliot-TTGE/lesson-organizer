<script lang="ts">
    interface Props {
        weekday: string,
        date: string,
        time: string,
        student: string,
        plan: string
    }

    let {weekday, date, time, student, plan} : Props = $props()
</script>

<style>
    p {
        color: darkorchid
    }
</style>

<div class='bg-neutral w-64 m-4 rounded'>
    <div class='flex flex-col p-2 space-y-2'>
        <p>{weekday}</p>
        <p>{date}:</p>
        <p>{time}:</p>
        <p>{student}</p>
        <div>
            <p>Today's plan:</p>
            <p class='min-h-24'>
                {plan}
            </p>
        </div>
        <div class='bg-accent mx-2 min-h-32'>
            <p>Card Concepts Taught</p>
        </div>
        <div class='bg-accent mx-2 min-h-32'>
            <p>Card Lesson Notes</p>
        </div>
    </div>
</div>