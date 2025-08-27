"use client";

import { signOut, useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User, LogOut, Settings, FileText, CreditCard, Loader2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
// AuthModal is temporarily commented out
// import AuthModal from "@/components/ui/AuthModal";

export function UserNav() {
  const { data: session, status } = useSession();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleSignOut = async () => {
    setIsLoggingOut(true);
    try {
      await signOut({ redirect: true, callbackUrl: "/" });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (status === "loading") {
    return (
      <div className="flex items-center justify-end">
        <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
      </div>
    );
  }

  if (status === "unauthenticated" || !session) {
    return (
      <>
        <div className="flex items-center justify-end gap-3">
          <Button
            variant="ghost"
            onClick={() => {
              setAuthMode('signin');
              setAuthModalOpen(true);
            }}
            className="text-gray-300 hover:text-white"
          >
            Sign In
          </Button>
          <Button
            onClick={() => {
              setAuthMode('signup');
              setAuthModalOpen(true);
            }}
            className="bg-green-500 hover:bg-green-600 text-white"
          >
            Sign Up
          </Button>
        </div>

        {/* AuthModal temporarily disabled
        <AuthModal
          isOpen={authModalOpen}
          onClose={() => setAuthModalOpen(false)}
          mode={authMode}
          onModeChange={setAuthMode}
        /> */}
      </>
    );
  }

  return (
    <div className="flex items-center justify-end gap-4">
      <span className="text-sm text-gray-400">
        {session.user?.email}
      </span>
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="relative h-10 w-10 rounded-full bg-gray-800 hover:bg-gray-700"
          >
            {session.user?.image ? (
              <img
                src={session.user.image}
                alt={session.user.name || "User"}
                className="h-10 w-10 rounded-full"
              />
            ) : (
              <div className="h-10 w-10 rounded-full bg-green-500 flex items-center justify-center">
                <User className="h-6 w-6 text-white" />
              </div>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56 bg-gray-900 border-gray-800" align="end">
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium text-white">
                {session.user?.name || "User"}
              </p>
              <p className="text-xs text-gray-400">
                {session.user?.email}
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator className="bg-gray-800" />
          
          <DropdownMenuItem asChild className="text-gray-300 hover:bg-gray-800 cursor-pointer">
            <Link href="/upload">
              <FileText className="mr-2 h-4 w-4" />
              <span>Dashboard</span>
            </Link>
          </DropdownMenuItem>
          
          <DropdownMenuItem asChild className="text-gray-300 hover:bg-gray-800 cursor-pointer">
            <Link href="/settings">
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </Link>
          </DropdownMenuItem>
          
          <DropdownMenuItem asChild className="text-gray-300 hover:bg-gray-800 cursor-pointer">
            <Link href="/settings/billing">
              <CreditCard className="mr-2 h-4 w-4" />
              <span>Billing</span>
            </Link>
          </DropdownMenuItem>
          
          <DropdownMenuSeparator className="bg-gray-800" />
          
          <DropdownMenuItem
            onClick={handleSignOut}
            disabled={isLoggingOut}
            className="text-red-400 hover:bg-gray-800 cursor-pointer"
          >
            {isLoggingOut ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <LogOut className="mr-2 h-4 w-4" />
            )}
            <span>Sign out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}