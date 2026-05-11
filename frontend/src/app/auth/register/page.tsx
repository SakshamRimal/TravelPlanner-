import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function RegisterPage() {
  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <h1 className="text-xl font-semibold">Create your account</h1>
      </CardHeader>
      <CardContent>
        <form className="grid gap-4">
          <input
            className="h-10 rounded-md border border-slate-200 px-3"
            placeholder="Name"
            type="text"
          />
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
          <Button type="submit">Register</Button>
        </form>
      </CardContent>
    </Card>
  );
}
