<script lang="ts">
  import { login } from '../../api/authentication';
  import { goto } from '$app/navigation';

  let email = "";
  let password = "";
  let errorMessage = "";

  async function handleLogin() {
    try {
      const response = await login(email, password);
      localStorage.setItem('token', response.access_token);
      goto('/lessons');
    } catch (error) {
      console.error('Error logging in:', error);
      errorMessage = 'An error occurred. Please try again.';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleLogin();
    }
  }
</script>

<div class="flex items-center justify-center min-h-screen bg-base-300">
  <div class="card w-96 bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Login</h2>
      {#if errorMessage}
        <div class="alert alert-error">
          <span>{errorMessage}</span>
        </div>
      {/if}
      <div class="form-control">
        <label class="label" for="email">
          <span class="label-text">Email</span>
        </label>
        <input
          id="email"
          type="email"
          bind:value={email}
          class="input input-bordered"
          placeholder="Enter your email"
          required
        />
      </div>
      <div class="form-control mt-4">
        <label class="label" for="password">
          <span class="label-text">Password</span>
        </label>
        <input
          id="password"
          type="password"
          bind:value={password}
          class="input input-bordered"
          placeholder="Enter your password"
          onkeydown={handleKeyDown}
          required
        />
      </div>
      <div class="form-control mt-6">
        <button class="btn btn-primary" onclick={handleLogin}>Login</button>
      </div>
    </div>
  </div>
</div>
