import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function ChatPage() {
  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <h1 className="text-xl font-semibold">AI Travel Assistant</h1>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div className="h-64 rounded-md border border-dashed border-slate-200 p-4 text-sm text-slate-500">
          Chat history appears here.
        </div>
        <form className="flex gap-2">
          <input
            className="h-10 flex-1 rounded-md border border-slate-200 px-3"
            placeholder="Ask about a destination or trip..."
          />
          <Button type="submit">Send</Button>
        </form>
      </CardContent>
    </Card>
  );
}
