"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const Spinner = () => {
  const [show, setShow] = useState(true);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setShow(true);
    const timeout = setTimeout(() => setShow(false), 500);
    return () => clearTimeout(timeout);
  }, [pathname]);

  return show ? (
    <div className="min-h-screen flex items-center justify-center bg-white/80 backdrop-blur-sm">
      <div className="spinner" />
    </div>
  ) : null;
};

export default function Loading() {
  return <Spinner />;
}

export const dynamic = "force-dynamic";