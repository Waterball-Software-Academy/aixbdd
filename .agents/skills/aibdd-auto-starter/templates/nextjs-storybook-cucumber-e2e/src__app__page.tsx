export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-zinc-50 p-8 dark:bg-black">
      <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
        It works!
      </h1>
      <p className="max-w-md text-center text-xs text-zinc-500 dark:text-zinc-400">
        Edit{" "}
        <code className="rounded bg-zinc-200 px-1.5 py-0.5 font-mono text-xs dark:bg-zinc-800">
          src/app/page.tsx
        </code>{" "}
        to start building.
      </p>
    </main>
  );
}
