import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

// Increase body size limit for audio uploads (Vercel Pro: 4.5 MB default, config below lifts it)
export const maxDuration = 300; // 5 min timeout for long processing

export async function POST(request: NextRequest) {
  const apiUrl = (process.env.MEETING_API_URL ?? "").replace(/\/$/, "");
  if (!apiUrl) {
    return NextResponse.json(
      { error: "MEETING_API_URL não configurado no servidor." },
      { status: 500 }
    );
  }

  const meetingName = request.nextUrl.searchParams.get("meeting_name") ?? "reuniao";

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json({ error: "Falha ao ler FormData." }, { status: 400 });
  }

  const upstream = await fetch(
    `${apiUrl}/transcribe?meeting_name=${encodeURIComponent(meetingName)}`,
    { method: "POST", body: formData }
  );

  const data = await upstream.json().catch(() => ({ error: "Resposta inválida do backend." }));
  return NextResponse.json(data, { status: upstream.status });
}
