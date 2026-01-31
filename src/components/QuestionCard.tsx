import { Question } from "../types";
import { getDifficultyColor, getDifficultyLabel } from "../utils/helpers";
import { Save, Trash2 } from "lucide-react";
import { convertFileSrc } from "@tauri-apps/api/core";
import clsx from "clsx";

interface QuestionCardProps {
    question: Question;
    isSelected?: boolean;
    onClick?: () => void;
    onDelete?: () => void;
    onSave?: () => void;
    mode: 'library' | 'analyze';
}

export default function QuestionCard({ question: q, isSelected, onClick, onDelete, onSave, mode }: QuestionCardProps) {
    return (
        <div
            onClick={onClick}
            className={clsx(
                "bg-white dark:bg-slate-800 border rounded-xl overflow-hidden hover:shadow-lg transition-all relative group cursor-pointer",
                isSelected ? "border-primary ring-2 ring-primary/20" : "border-slate-200 dark:border-slate-700",
                mode === 'analyze' ? "flex flex-row p-4 gap-4 items-start" : "flex flex-col"
            )}
        >
            {/* Image Section */}
            <div className={clsx(
                "bg-slate-100 dark:bg-slate-900 relative shrink-0 overflow-hidden",
                mode === 'library' ? "aspect-video w-full" : "w-16 h-16 rounded-lg flex items-center justify-center"
            )}>
                {mode === 'library' ? (
                    q.image_base64 && <img src={q.image_base64} className="w-full h-full object-contain" />
                ) : (
                    q.image && <img src={q.image.startsWith('data:') ? q.image : convertFileSrc(q.image)} className="w-full h-full object-contain" />
                )}

                {/* Page Badge */}
                {mode === 'library' && (
                    <div className="absolute top-2 right-2 flex gap-1">
                        {q.topic && <span className="bg-white/90 text-slate-700 text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm">{q.topic}</span>}
                        <span className={clsx("text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm text-white", q.difficulty && q.difficulty > 3 ? "bg-red-500" : (q.difficulty === 3 ? "bg-yellow-500" : "bg-emerald-500"))}>
                            Sayfa {q.page}
                        </span>
                    </div>
                )}

                {/* Checkbox (Only Library) */}
                {mode === 'library' && (
                    <div className={clsx(
                        "absolute top-2 left-2 w-5 h-5 rounded border border-slate-300 bg-white flex items-center justify-center transition-opacity",
                        isSelected ? "bg-primary border-primary opacity-100" : "opacity-0 group-hover:opacity-100"
                    )}>
                        {isSelected && <span className="text-white text-xs">✓</span>}
                    </div>
                )}
            </div>

            {/* Content Section */}
            <div className={clsx("flex-1 min-w-0", mode === 'library' ? "p-4 flex flex-col h-40" : "")}>
                {/* Analyze Header */}
                {mode === 'analyze' && (
                    <div className="flex items-start justify-between mb-2">
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-bold text-slate-400">Sayfa {q.page}</span>
                            <div className="flex gap-1">
                                {q.topic && <span className="text-[10px] uppercase tracking-wider font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{q.topic}</span>}
                                <span className={clsx("text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded", getDifficultyColor(q.difficulty))}>
                                    {getDifficultyLabel(q.difficulty)}
                                </span>
                            </div>
                        </div>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                            {onSave && (
                                <button
                                    className="p-1 hover:bg-emerald-50 rounded text-emerald-500"
                                    onClick={(e) => { e.stopPropagation(); onSave(); }}
                                >
                                    <Save size={16} />
                                </button>
                            )}
                        </div>
                    </div>
                )}

                <p className={clsx("text-sm font-medium text-slate-800 dark:text-slate-200 line-clamp-3", mode === 'library' ? "mb-2 flex-1" : "")}>
                    {q.text}
                </p>

                {/* Library Footer */}
                {mode === 'library' && (
                    <div className="flex justify-between items-center mt-auto pt-4 border-t border-slate-100 dark:border-slate-800">
                        <span className={clsx("text-xs font-bold px-2 py-1 rounded", getDifficultyColor(q.difficulty))}>
                            {getDifficultyLabel(q.difficulty)} ({q.difficulty || "?"}/5)
                        </span>
                        {onDelete && (
                            <button
                                className="text-xs text-red-500 hover:underline z-20"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDelete();
                                }}
                            >
                                Sil
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
