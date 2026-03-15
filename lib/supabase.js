import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://btschxgghvblmohddqcj.supabase.co";
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ0c2NoeGdnaHZibG1vaGRkcWNqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxNTUwNjMsImV4cCI6MjA4ODczMTA2M30.sgrwlNGiWovs6Y93lzAvkjeEsiNWbQqC5E3Pw9UjJxs";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
