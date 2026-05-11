import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function LoginPage() {
  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <h1 className="text-xl font-semibold">Welcome back</h1>
      </CardHeader>
      <CardContent>
        <form className="grid gap-4">
          <input
            className="h-10 rounded-md border border-slate-200 px-3"
            placeholder="Email"
            type="email"
          />
          <input
            className="h-10 rounded-md border border-slate-200 px-3"
            placeholder="Password"
            type="password"
          />
          <Button type="submit">Login</Button>
        </form>
      </CardContent>
    </Card>
  );
}
