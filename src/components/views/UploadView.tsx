import { Upload, Loader2, FileText, RefreshCw, Save } from "lucide-react";
import { Question } from "../../types";
import QuestionCard from "../QuestionCard";
import { motion } from "framer-motion";

interface UploadViewProps {
    loading: boolean;
    loadingText: string;
    progress?: { current: number, total: number };
    pdfPath: string | null;
    questions: Question[];
    error: string | null;
    onUpload: () => void;
    onSaveQuestion: (q: Question) => void;
    onSaveAll: () => void;
    onReset: () => void;
}

export default function UploadView({
    loading, loadingText, progress, pdfPath, questions, error, onUpload, onSaveQuestion, onSaveAll, onReset
}: UploadViewProps) {

    if (loading) {
        return (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full flex flex-col items-center justify-center">
                {progress && progress.total > 0 ? (
                    <div className="w-64">
                        <div className="flex justify-between text-xs font-bold text-slate-500 mb-2">
                            <span>Sayfa {progress.current} / {progress.total}</span>
                            <span>{Math.round((progress.current / progress.total) * 100)}%</span>
                        </div>
                        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-primary transition-all duration-300"
                                style={{ width: `${(progress.current / progress.total) * 100}%` }}
                            ></div>
                        </div>
                        <p className="text-center text-slate-500 text-sm mt-4 font-medium animate-pulse">Sorular Ayrıştırılıyor...</p>
                    </div>
                ) : (
                    <>
                        <Loader2 className="animate-spin text-primary mb-4" size={48} />
                        <h3 className="text-xl font-bold text-slate-800">{loadingText}</h3>
                    </>
                )}
            </motion.div>
        );
    }

    if (questions.length > 0) {
        // Analyze Mode
        return (
            <motion.div key="analyze" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full grid grid-cols-2 gap-6">
                {/* Left: Preview */}
                <div className="bg-slate-100 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center relative overflow-hidden">
                    <FileText size={64} className="text-slate-300 mb-4" />
                    <p className="text-slate-400 font-medium">PDF Önizleme</p>
                    <p className="text-slate-500 text-sm mt-2">{pdfPath}</p>
                </div>

                {/* Right: List */}
                <div className="overflow-y-auto pr-2 space-y-4">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="font-bold text-lg">Tespit Edilen Sorular ({questions.length})</h3>
                        <div className="flex gap-2">
                            <button onClick={onSaveAll} className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1">
                                <Save size={16} /><span>Tümünü Kaydet</span>
                            </button>
                            <button onClick={onReset} className="text-slate-500 hover:text-primary p-2 transition-colors">
                                <RefreshCw size={18} />
                            </button>
                        </div>
                    </div>
                    {questions.map((q, i) => (
                        <QuestionCard
                            key={i}
                            question={q}
                            mode="analyze"
                            onSave={() => onSaveQuestion(q)}
                        />
                    ))}
                </div>
            </motion.div>
        );
    }

    // Upload Mode
    return (
        <motion.div key="upload" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto">
            <div onClick={onUpload} className="w-full bg-white dark:bg-slate-900 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-16 flex flex-col items-center text-center cursor-pointer hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-all group">
                <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform duration-300">
                    <Upload size={40} />
                </div>
                <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">PDF Dosyanızı Buraya Bırakın</h3>
                <p className="text-slate-500 max-w-md">Yapay zeka destekli soru ayrıştırması için belgeyi sürükleyin veya tıklayın.</p>
            </div>
            {error && <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-xl border border-red-200 max-w-md text-sm">⚠️ {error}</div>}
        </motion.div>
    );
}
