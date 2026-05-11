import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function Navbar() {
  return (
    <nav className="border-b border-slate-200 bg-white">
      <div className="container-page flex h-16 items-center justify-between">
        <Link href="/" className="text-lg font-semibold">
          TravelPlanner
        </Link>
        <div className="flex items-center gap-3">
          <Link href="/planner" className="text-sm text-slate-600">
            Plan a trip
          </Link>
          <Link href="/chat" className="text-sm text-slate-600">
            AI chat
          </Link>
          <Button asChild variant="outline" size="sm">
            <Link href="/auth/login">Login</Link>
          </Button>
        </div>
      </div>
    </nav>
  );
}
