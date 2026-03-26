import { supabase } from "./supabase";

export async function trackEvent({
  eventName,
  page = null,
  requestId = null,
  formula = null,
}) {
  try {
    await supabase.from("events").insert([
      {
        event_name: eventName,
        page,
        request_id: requestId,
        formula,
      },
    ]);
  } catch (error) {
    console.error("Tracking error:", error.message);
  }
}