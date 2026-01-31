import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { motion } from "framer-motion";
import { Archive, User, Calendar, FileText, ChevronRight, Key, X, CheckCircle } from "lucide-react";
import { Question } from "../../types";
import QuestionCard from "../QuestionCard";

interface TestRecord {
    id: number;
    date: string;
    student_name: string | null;
    question_count: number;
}

export default function ArchiveView() {
    const [tests, setTests] = useState<TestRecord[]>([]);
    const [selectedTestId, setSelectedTestId] = useState<number | null>(null);
    const [testQuestions, setTestQuestions] = useState<Question[]>([]);
    const [loading, setLoading] = useState(false);

    // Answer Key State
    const [answerKey, setAnswerKey] = useState<any>(null);
    const [showKeyModal, setShowKeyModal] = useState(false);
    const [keyLoading, setKeyLoading] = useState(false);

    useEffect(() => {
        loadTests();
    }, []);

    useEffect(() => {
        if (selectedTestId) {
            loadTestQuestions(selectedTestId);
            setAnswerKey(null); // Reset key when test changes
        } else {
            setTestQuestions([]);
        }
    }, [selectedTestId]);

    const loadTests = async () => {
        try {
            // list_tests returns Vec<(i32, String, Option<String>, i32)>
            const res = await invoke<[number, string, string | null, number][]>('list_tests');
            const mapped = res.map(([id, date, student_name, question_count]) => ({
                id, date, student_name, question_count
            }));
            setTests(mapped);
        } catch (e) { console.error(e); }
    }

    const loadTestQuestions = async (id: number) => {
        setLoading(true);
        try {
            const res = await invoke<Question[]>('get_test_questions', { testId: id });
            setTestQuestions(res);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    }

    const handleGenerateKey = async () => {
        if (!selectedTestId) return;
        setKeyLoading(true);
        try {
            const res = await invoke<string>('generate_answer_key', { testId: selectedTestId });
            const parsed = JSON.parse(res);
            setAnswerKey(parsed);
            setShowKeyModal(true);
        } catch (e) {
            alert("Cevap anahtarı oluşturulamadı: " + e);
        } finally {
            setKeyLoading(false);
        }
    }

    return (
        <motion.div key="archive" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex gap-6 overflow-hidden relative">

            {/* Left: List */}
            <div className="w-80 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden shrink-0">
                <div className="p-4 border-b border-slate-100 dark:border-slate-700 font-bold flex items-center gap-2 text-slate-700 dark:text-slate-300">
                    <Archive size={18} />
                    Geçmiş Testler
                </div>

                <div className="flex-1 overflow-y-auto">
                    {tests.length === 0 ? (
                        <div className="p-8 text-center text-slate-400 text-sm">
                            Kayıtlı test bulunamadı.
                        </div>
                    ) : (
                        tests.map(t => (
                            <div
                                key={t.id}
                                onClick={() => setSelectedTestId(t.id)}
                                className={`p-4 border-b border-slate-50 dark:border-slate-800 cursor-pointer transition-colors ${selectedTestId === t.id ? 'bg-primary/5 border-l-4 border-l-primary' : 'hover:bg-slate-50 dark:hover:bg-slate-700'}`}
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="font-bold text-slate-700 dark:text-slate-200 text-sm">Test #{t.id}</span>
                                    <span className="text-[10px] text-slate-400">{t.date.substring(0, 16)}</span>
                                </div>
                                <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
                                    <User size={12} />
                                    {t.student_name ? <span className="text-blue-600 font-medium">{t.student_name}</span> : "Genel"}
                                </div>
                                <div className="flex items-center gap-1 text-xs text-slate-400">
                                    <FileText size={12} />
                                    {t.question_count} Soru
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Right: Details */}
            <div className="flex-1 overflow-hidden flex flex-col bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-slate-200 dark:border-slate-800 relative">
                {selectedTestId ? (
                    <>
                        <div className="p-4 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center shadow-sm z-10">
                            <div>
                                <h3 className="font-bold text-lg">Test Önizleme (#{selectedTestId})</h3>
                                <div className="text-sm text-slate-500">{testQuestions.length} Soru</div>
                            </div>
                            <button
                                onClick={handleGenerateKey}
                                disabled={keyLoading}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg font-bold text-sm flex items-center gap-2 transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
                            >
                                {keyLoading ? <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div> : <Key size={16} />}
                                {keyLoading ? "Oluşturuluyor..." : "Cevap Anahtarı"}
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4">
                            {loading ? (
                                <div className="flex items-center justify-center h-full">Yükleniyor...</div>
                            ) : (
                                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 pb-10">
                                    {testQuestions.map((q, i) => (
                                        <QuestionCard key={i} question={q} mode="analyze" />
                                    ))}
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-400">
                        <Archive size={48} className="mb-4 opacity-20" />
                        <p>Detaylarını görmek için soldan bir test seçin.</p>
                    </div>
                )}
            </div>

            {/* Answer Key Modal */}
            {showKeyModal && answerKey && (
                <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 animate-in fade-in duration-200">
                    <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-2xl shadow-2xl flex flex-col max-h-[80vh] overflow-hidden">
                        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-800/50">
                            <h3 className="font-bold flex items-center gap-2"><Key size={18} className="text-emerald-500" /> Cevap Anahtarı</h3>
                            <button onClick={() => setShowKeyModal(false)} className="p-2 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full"><X size={18} /></button>
                        </div>
                        <div className="p-0 overflow-y-auto flex-1">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-100 dark:bg-slate-800 text-xs text-slate-500 uppercase">
                                    <tr>
                                        <th className="px-6 py-3">Soru</th>
                                        <th className="px-6 py-3">Cevap</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                                    {answerKey.answers?.map((a: any, i: number) => (
                                        <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                            <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">#{a.q_num}</td>
                                            <td className="px-6 py-3 font-bold text-emerald-600 dark:text-emerald-400">{a.answer}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {answerKey.answers?.length === 0 && (
                                <div className="p-6 text-center text-slate-400">Cevap bulunamadı veya AI hata verdi.</div>
                            )}
                        </div>
                        <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 text-center">
                            <button onClick={() => window.print()} className="text-primary hover:underline text-xs">Yazdır / PDF Olarak Kaydet</button>
                        </div>
                    </div>
                </div>
            )}

        </motion.div>
    );
}
