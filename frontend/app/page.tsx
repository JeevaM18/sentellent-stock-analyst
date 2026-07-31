import UserAvatar from "@/components/auth/UserAvatar";

export default function Home() {
  return (
    <main className="flex-1 flex flex-col items-center justify-center p-6 sm:p-12 relative overflow-hidden">
      {/* Subtle background glow effect */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/15 blur-3xl rounded-full pointer-events-none"></div>
      
      <div className="z-10 w-full flex flex-col items-center">
        <UserAvatar />
      </div>
    </main>
  );
}
