import React, { useState, useEffect, useRef, useCallback } from "react";
import { apiUrl } from "../utils/api";

interface ChatDrawerProps {
  userId: string;
  userRole: "admin" | "user";
  targetUserId?: string; // For admin, the user to chat with
  onClose: () => void;
}

interface ChatUser {
  name: string;
  id: string;
  username: string;
}

const ChatDrawer: React.FC<ChatDrawerProps> = ({
  userId,
  userRole,
  targetUserId,
  onClose,
}) => {
  // tokens are stored in localStorage under 'access_token'
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [adminTargetId, setAdminTargetId] = useState(targetUserId || "");
  const [userList, setUserList] = useState<ChatUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<ChatUser | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fetchUserList = useCallback(async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(apiUrl("/api/admin/users/only-users"), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      const users = data.users || [];
      setUserList(users);
    } catch (error) {
      console.error("Failed to fetch UserList: ", error);
    }
  }, []);

  const fetchMessages = useCallback(async () => {
    try {
      const id = userRole === "admin" ? adminTargetId : userId;
      if (!id) return;
      const token = localStorage.getItem("access_token");
      const res = await fetch(apiUrl(`/api/chat/messages?user_id=${id}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error("Failed to fetch messages: ", error);
    }
  }, [userRole, adminTargetId, userId]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    setLoading(true);
    try {
      const payload = {
        to_id: userRole === "admin" ? adminTargetId : "admin",
        to_role: userRole === "admin" ? "user" : "admin",
        content: input.trim(),
      };
      const token = localStorage.getItem("access_token");
      const res = await fetch(apiUrl("/api/chat/send"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setInput("");
        fetchMessages();
      }
    } finally {
      setLoading(false);
    }
  };
  // Fetch user list for admin
  useEffect(() => {
    if (userRole === "admin") fetchUserList();
  }, [userRole]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (!userId || (userRole === "admin" && !adminTargetId)) return;
    fetchMessages();
    const interval = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        fetchMessages();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [userId, userRole, adminTargetId, fetchMessages]);

  useEffect(() => {
    if (!isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isMinimized]);

  return (
    <div className="fixed bottom-0 right-4 z-[9999] flex items-end font-sans">
      <div
        className={`
        flex flex-col bg-white dark:bg-slate-900 
        shadow-[0_-4px_24px_rgba(0,0,0,0.15)] border border-gray-200 dark:border-slate-700
        rounded-t-xl transition-all duration-300 ease-in-out
        ${isMinimized ? "h-12" : "h-[480px]"} 
        ${userRole === "admin" && !isMinimized ? "w-[480px]" : "w-72 sm:w-80"}
      `}
      >
        {/* Header: the toggle and the close control are siblings, since a button cannot contain a button */}
        <div className="flex items-center border-b border-yellow-500 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/50 rounded-t-xl">
          <button
            type="button"
            aria-expanded={!isMinimized}
            onClick={() => setIsMinimized(!isMinimized)}
            className="flex-1 min-w-0 text-left bg-transparent border-none flex items-center justify-between pl-4 pr-3 py-3"
          >
            <div className="flex items-center gap-2 truncate">
              <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-bold text-gray-800 dark:text-gray-100 truncate">
                {userRole === "admin"
                  ? selectedUser
                    ? `Chat: ${selectedUser.name}`
                    : "Users"
                  : "Support"}
              </span>
            </div>
            <span className="text-gray-400 text-xs">
              {isMinimized ? "Expand" : "Hide"}
            </span>
          </button>
          <button
            type="button"
            aria-label="Close chat"
            onClick={onClose}
            className="pr-4 text-gray-400 hover:text-red-500 transition-colors text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        {!isMinimized && (
          <div className="flex flex-1 overflow-hidden">
            {/* Improved Admin Sidebar */}
            {userRole === "admin" && (
              <div className="w-40 border-r border-yellow-500 dark:border-slate-800 flex flex-col bg-gray-50/50 dark:bg-slate-950/50">
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                  {userList.map((user) => (
                    <div
                      key={user.id}
                      className={`cursor-pointer px-3 py-3 border-b border-yellow-500 dark:border-slate-800 transition-colors
                        ${
                          selectedUser?.id === user.id
                            ? "bg-yellow-400 text-black font-bold"
                            : "hover:bg-gray-200/50 dark:hover:bg-slate-800 text-gray-700 dark:text-gray-300 font-medium"
                        }`}
                      onClick={() => {
                        setSelectedUser(user);
                        setAdminTargetId(user.id);
                      }}
                    >
                      <div className="truncate text-xs leading-tight">
                        {user.name || user.username || "User"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Message Area */}
            <div className="flex-1 flex flex-col bg-white dark:bg-slate-900 min-w-0">
              <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                {messages.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-xs text-gray-400 italic">
                    No messages yet.
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div
                      key={msg._id || idx}
                      className={`flex ${msg.from_id === userId ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[88%] px-3 py-2 rounded-2xl text-[13px] shadow-sm leading-snug
                        ${
                          msg.from_id === userId
                            ? "bg-yellow-400 text-black rounded-tr-none"
                            : "bg-gray-100 dark:bg-slate-800 text-gray-800 dark:text-gray-200 rounded-tl-none"
                        }`}
                      >
                        {msg.content}
                        <div className="text-[9px] opacity-50 mt-1 text-right">
                          {msg.timestamp
                            ? new Date(msg.timestamp).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            : ""}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Bar */}
              <div className="p-3 border-t border-yellow-500 dark:border-slate-800">
                <div className="relative flex items-center">
                  <input
                    type="text"
                    className="w-full pl-4 pr-10 py-2 bg-gray-100 dark:bg-slate-800 border-none rounded-full text-sm focus:ring-1 focus:ring-yellow-400 text-gray-900 dark:text-white"
                    placeholder="Message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") sendMessage();
                    }}
                    disabled={
                      loading || (userRole === "admin" && !adminTargetId)
                    }
                  />
                  <button
                    type="button"
                    onClick={sendMessage}
                    disabled={
                      loading ||
                      !input.trim() ||
                      (userRole === "admin" && !adminTargetId)
                    }
                    aria-label="Send message"
                    className="absolute right-1 p-1.5 text-yellow-600 dark:text-yellow-400 disabled:opacity-20 hover:scale-110 transition-transform"
                  >
                    <svg
                      className="w-5 h-5 rotate-90"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #475569; }
      `}</style>
    </div>
  );
};

export default ChatDrawer;
