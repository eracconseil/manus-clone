"use client";
import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://manus-clone-production.up.railway.app";

export interface Profile {
  plan: "free" | "pro" | "business";
  tasks_used: number;
  tasks_limit: number;
  email: string;
}

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      const res = await fetch(`${API_URL}/api/billing/profile`);
      if (res.ok) setProfile(await res.json());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  return { profile, loading, refresh };
}
