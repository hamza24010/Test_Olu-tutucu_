import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { motion } from "framer-motion";
import { Users, UserPlus, Trash2, Search } from "lucide-react";

interface Student {
    id: number;
    name: string;
}

export default function StudentsView() {
    const [students, setStudents] = useState<Student[]>([]);
    const [newStudentName, setNewStudentName] = useState("");
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        loadStudents();
    }, []);

    const loadStudents = async () => {
        try {
            // list_students returns Vec<(i32, String)> -> we need to map to object
            const res = await invoke<[number, string][]>('list_students');
            const mapped = res.map(([id, name]) => ({ id, name }));
            setStudents(mapped);
        } catch (e) {
            console.error(e);
        }
    }

    const handleAddStudent = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newStudentName.trim()) return;

        setLoading(true);
        try {
            await invoke('add_student', { name: newStudentName });
            setNewStudentName("");
            loadStudents();
        } catch (e: any) {
            alert("Hata: " + e);
        } finally {
            setLoading(false);
        }
    }

    const handleDeleteStudent = async (id: number) => {
        if (!confirm("Öğrenciyi silmek istediğinize emin misiniz? Çözdüğü soru kayıtları da silinecektir.")) return;
        try {
            await invoke('delete_student', { id });
            loadStudents();
        } catch (e) { alert("Silme hatası: " + e); }
    }

    const filteredStudents = students.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()));

    return (
        <motion.div key="students" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex flex-col gap-6 overflow-hidden">

            {/* Top Bar: Add & Search */}
            <div className="flex flex-col md:flex-row gap-4 bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm shrink-0">
                <form onSubmit={handleAddStudent} className="flex gap-2 flex-1">
                    <div className="relative flex-1">
                        <Users className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                        <input
                            type="text"
                            placeholder="Yeni Öğrenci Adı"
                            className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 outline-none focus:ring-2 focus:ring-primary/20"
                            value={newStudentName}
                            onChange={(e) => setNewStudentName(e.target.value)}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading || !newStudentName}
                        className="bg-primary text-white px-6 rounded-xl font-bold flex items-center gap-2 hover:bg-primary/90 disabled:opacity-50 transition-all shadow-lg shadow-primary/20 whitespace-nowrap"
                    >
                        <UserPlus size={20} />
                        Ekle
                    </button>
                </form>

                <div className="relative w-full md:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        type="text"
                        placeholder="Öğrenci Ara..."
                        className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 outline-none focus:ring-2 focus:ring-primary/20"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* List */}
            <div className="flex-1 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col shadow-sm">
                <div className="p-4 border-b border-slate-100 dark:border-slate-700 font-bold text-slate-500 text-sm flex justify-between">
                    <span>Öğrenci Listesi ({filteredStudents.length})</span>
                </div>
                <div className="overflow-y-auto flex-1 p-2">
                    {filteredStudents.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {filteredStudents.map(s => (
                                <div key={s.id} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-100 dark:border-slate-800 hover:border-primary/30 transition-colors group">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-lg">
                                            {s.name.charAt(0).toUpperCase()}
                                        </div>
                                        <span className="font-medium text-slate-700 dark:text-slate-200">{s.name}</span>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteStudent(s.id)}
                                        className="text-slate-400 hover:text-red-500 hover:bg-red-50 p-2 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-slate-400">
                            <Users size={48} className="mb-4 opacity-20" />
                            <p>Öğrenci bulunamadı.</p>
                        </div>
                    )}
                </div>
            </div>

        </motion.div>
    );
}
