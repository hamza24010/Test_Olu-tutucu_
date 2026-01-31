import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Question } from "../../types";
import QuestionCard from "../QuestionCard";
import { motion } from "framer-motion";
import { Sparkles, RefreshCw, FileText, SlidersHorizontal, Settings2 } from "lucide-react";

interface CreateTestViewProps {
    onExport: (questions: Question[], studentId: number | null) => void;
}

export default function CreateTestView({ onExport }: CreateTestViewProps) {
    // Settings State
    const [topics, setTopics] = useState<String[]>([]);
    const [selectedTopic, setSelectedTopic] = useState<string>("");
    const [difficulty, setDifficulty] = useState<number | null>(null); // null = mixed
    const [questionCount, setQuestionCount] = useState<number>(20);

    // Student Selection
    const [students, setStudents] = useState<{ id: number, name: string }[]>([]);
    const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);

    // Result State
    const [generatedQuestions, setGeneratedQuestions] = useState<Question[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadTopics();
        loadStudents();
    }, []);

    const loadTopics = async () => {
        try {
            const res = await invoke<string[]>('get_topics');
            setTopics(res);
        } catch (e) { console.error(e); }
    }

    const loadStudents = async () => {
        try {
            const res = await invoke<[number, string][]>('list_students');
            setStudents(res.map(([id, name]) => ({ id, name })));
        } catch (e) { console.error(e); }
    }

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const res = await invoke<Question[]>('generate_test', {
                topic: selectedTopic || null,
                difficulty: difficulty,
                count: questionCount,
                studentId: selectedStudentId // Optional
            });
            setGeneratedQuestions(res);
        } catch (e: any) {
            alert("Hata: " + e);
        } finally {
            setLoading(false);
        }
    }

    return (
        <motion.div key="create-test" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex gap-6 overflow-hidden">

            {/* Left Panel: Settings */}
            <div className="w-80 flex flex-col gap-6 overflow-y-auto pr-2 pb-10">
                <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
                    {/* Student Selection (New) */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Öğrenci (Opsiyonel)</label>
                        <select
                            value={selectedStudentId || ""}
                            onChange={(e) => setSelectedStudentId(e.target.value ? parseInt(e.target.value) : null)}
                            className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 outline-none focus:ring-2 focus:ring-primary/20 text-sm"
                        >
                            <option value="">Öğrenci Seçilmedi (Genel)</option>
                            {students.map(s => (
                                <option key={s.id} value={s.id}>{s.name}</option>
                            ))}
                        </select>
                        <p className="text-[10px] text-slate-400 mt-1 leading-tight">
                            Öğrenci seçerseniz, daha önce çözdüğü sorular testte çıkmaz.
                        </p>
                    </div>

                    <hr className="border-slate-100 dark:border-slate-700 mb-6" />

                    <div className="flex items-center gap-2 mb-6">
                        <SlidersHorizontal className="text-primary" />
                        <h2 className="font-bold text-lg">Test Ayarları</h2>
                    </div>

                    {/* Topic Selection */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Konu Seçimi</label>
                        <select
                            value={selectedTopic}
                            onChange={(e) => setSelectedTopic(e.target.value)}
                            className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 outline-none focus:ring-2 focus:ring-primary/20"
                        >
                            <option value="">Karışık (Tüm Konular)</option>
                            {topics.map((t, i) => (
                                <option key={i} value={t as string}>{t}</option>
                            ))}
                        </select>
                    </div>

                    {/* Difficulty Selection */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Zorluk Seviyesi</label>
                        <div className="grid grid-cols-4 gap-2">
                            <button
                                onClick={() => setDifficulty(null)}
                                className={`p-2 rounded-lg text-xs font-bold transition-all ${difficulty === null ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                            >
                                Karışık
                            </button>
                            <button
                                onClick={() => setDifficulty(1)}
                                className={`p-2 rounded-lg text-xs font-bold transition-all ${difficulty === 1 ? 'bg-green-500 text-white' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}
                            >
                                Kolay
                            </button>
                            <button
                                onClick={() => setDifficulty(3)}
                                className={`p-2 rounded-lg text-xs font-bold transition-all ${difficulty === 3 ? 'bg-yellow-500 text-white' : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'}`}
                            >
                                Orta
                            </button>
                            <button
                                onClick={() => setDifficulty(5)}
                                className={`p-2 rounded-lg text-xs font-bold transition-all ${difficulty === 5 ? 'bg-red-500 text-white' : 'bg-red-100 text-red-700 hover:bg-red-200'}`}
                            >
                                Zor
                            </button>
                        </div>
                    </div>

                    {/* Count Selection */}
                    <div className="mb-8">
                        <label className="flex justify-between text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            <span>Soru Sayısı</span>
                            <span className="text-primary font-bold">{questionCount}</span>
                        </label>
                        <input
                            type="range"
                            min="5"
                            max="50"
                            step="5"
                            value={questionCount}
                            onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary"
                        />
                        <div className="flex justify-between text-xs text-slate-400 mt-1">
                            <span>5</span>
                            <span>50</span>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={loading}
                        className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-slate-900/20 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? <RefreshCw className="animate-spin" /> : <Sparkles size={20} />}
                        {loading ? "Oluşturuluyor..." : "Test Oluştur"}
                    </button>
                </div>
            </div>

            {/* Right Panel: Results */}
            <div className="flex-1 flex flex-col min-w-0 bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 overflow-hidden">
                {generatedQuestions.length > 0 ? (
                    <>
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-xl font-bold text-slate-800 dark:text-white">Oluşturulan Test</h3>
                                <p className="text-sm text-slate-500">{generatedQuestions.length} soru seçildi.</p>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={handleGenerate}
                                    className="p-2 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors"
                                    title="Yeniden Dağıt"
                                >
                                    <RefreshCw size={20} />
                                </button>
                                <button
                                    onClick={() => onExport(generatedQuestions, selectedStudentId)}
                                    className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-primary/20 transition-all"
                                >
                                    <FileText size={18} />
                                    PDF YAZDIR
                                </button>
                            </div>
                        </div>

                        <div className="overflow-y-auto flex-1 pr-2">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-10">
                                {generatedQuestions.map((q, i) => (
                                    <QuestionCard
                                        key={i}
                                        question={q}
                                        mode="analyze" // Use analyze mode for compact view
                                    />
                                ))}
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
                        <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                            <Settings2 size={32} />
                        </div>
                        <h3 className="text-lg font-bold text-slate-600">Henüz Test Oluşturulmadı</h3>
                        <p className="max-w-xs text-center mt-2">Sol menüden konu ve zorluk seviyesi seçerek yapay zeka destekli test oluşturabilirsiniz.</p>
                    </div>
                )}
            </div>

        </motion.div>
    );
}
