import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Question } from "../../types";
import QuestionCard from "../QuestionCard";
import { motion } from "framer-motion";

interface LibraryViewProps {
    // No longer passing questions directly
    selectedIds: any[];
    onToggleSelection: (id: any) => void;
    onDelete: (ids: any[]) => void;
}

export default function LibraryView({ selectedIds, onToggleSelection, onDelete }: LibraryViewProps) {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [loading, setLoading] = useState(false);

    // Pagination State
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const limit = 20;

    // Filters
    const [searchTerm, setSearchTerm] = useState("");
    const [filterTopic, setFilterTopic] = useState<string>("");
    const [filterDifficulty, setFilterDifficulty] = useState<number | null>(null);

    useEffect(() => {
        loadData();
    }, [page, searchTerm, filterTopic, filterDifficulty]); // Reload when any dependency changes

    // Debounce Search (Simple)
    useEffect(() => {
        const timer = setTimeout(() => {
            if (page !== 1) setPage(1); // Reset page on new search
            else loadData();
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await invoke<{ questions: Question[], total: number }>('list_questions_paginated', {
                page,
                limit,
                search: searchTerm,
                topic: filterTopic || null,
                difficulty: filterDifficulty
            });
            setQuestions(res.questions);
            setTotalPages(Math.ceil(res.total / limit));
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }

    // Handle Delete Wrapper to reload
    const handleDelete = (ids: any[]) => {
        onDelete(ids);
        // Optimistic update or reload? Let's reload after short delay or wait for parent
        // Actually parent handleDelete executes delete command. We should reload here.
        setTimeout(loadData, 500);
    };

    return (
        <motion.div key="library" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full flex flex-col">
            {/* Filter Bar */}
            <div className="mb-4 flex gap-4 shrink-0 flex-wrap">
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                    <input
                        type="text"
                        placeholder="Soru metni ara..."
                        className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {/* Topic Filter */}
                <input
                    type="text"
                    placeholder="Konu (Opsiyonel)"
                    value={filterTopic}
                    onChange={(e) => { setFilterTopic(e.target.value); setPage(1); }}
                    className="w-40 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm"
                />

                {/* Difficulty Filter */}
                <select
                    title="Zorluk"
                    value={filterDifficulty || ""}
                    onChange={(e) => { setFilterDifficulty(e.target.value ? parseInt(e.target.value) : null); setPage(1); }}
                    className="w-32 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm"
                >
                    <option value="">Tüm Zorluklar</option>
                    <option value="1">Kolay (1-2)</option>
                    <option value="3">Orta (3)</option>
                    <option value="5">Zor (4-5)</option>
                </select>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto pb-4 relative">
                {loading ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : null}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {questions.map((q) => (
                        <QuestionCard
                            key={q.id}
                            question={q}
                            mode="library"
                            isSelected={selectedIds.includes(q.id)}
                            onClick={() => onToggleSelection(q.id)}
                            onDelete={() => handleDelete([q.id])}
                        />
                    ))}
                    {!loading && questions.length === 0 && (
                        <div className="col-span-full text-center py-20 text-slate-400">Soru bulunamadı.</div>
                    )}
                </div>
            </div>

            {/* Pagination Controls */}
            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between shrink-0">
                <span className="text-sm text-slate-500">Sayfa {page} / {totalPages || 1}</span>
                <div className="flex gap-2">
                    <button
                        disabled={page <= 1}
                        onClick={() => setPage(p => p - 1)}
                        className="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <button
                        disabled={page >= totalPages}
                        onClick={() => setPage(p => p + 1)}
                        className="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronRight size={20} />
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
