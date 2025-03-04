<script lang="ts">
  let email = "";
  let password = "";

  function handleLogin() {
    // Implement login logic here
    console.log("Logging in with", email, password);
  }
</script>

<div class="flex items-center justify-center min-h-screen bg-base-300">
  <div class="card w-96 bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Login</h2>
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
          required
        />
      </div>
      <div class="form-control mt-6">
        <button class="btn btn-primary" on:click={handleLogin}>Login</button>
      </div>
    </div>
  </div>
</div>
