import { Plus, Trash2, Edit2 } from "lucide-react";
import { Template } from "../../types";
import { motion } from "framer-motion";

interface TemplatesViewProps {
    templates: Template[];
    onDelete: (id: number) => void;
    onUpload: () => void;
    onEdit: (t: Template) => void;
}

export default function TemplatesView({ templates, onDelete, onUpload, onEdit }: TemplatesViewProps) {
    return (
        <motion.div key="templates" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex flex-col">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 overflow-y-auto pb-10">
                {templates.map(t => (
                    <div key={t.id} className="group bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden relative shadow-sm hover:shadow-lg transition-all">
                        <div className="aspect-[1/1.4] bg-slate-100 relative">
                            <img src={t.preview_image} className="w-full h-full object-cover" />
                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                <button onClick={() => onEdit(t)} className="bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600"><Edit2 size={20} /></button>
                                <button onClick={() => onDelete(t.id)} className="bg-red-500 text-white p-2 rounded-full hover:bg-red-600"><Trash2 size={20} /></button>
                            </div>
                            {/* Safe Area Visualization */}
                            {(() => {
                                try {
                                    const m = JSON.parse(t.margins_json);
                                    // 0-1000 scale to %
                                    const style = {
                                        top: `${m.top / 10}%`,
                                        left: `${m.left / 10}%`,
                                        width: `${(m.right - m.left) / 10}%`,
                                        height: `${(m.bottom - m.top) / 10}%`,
                                    };
                                    return <div className="absolute border-2 border-emerald-500/50 bg-emerald-500/10 pointer-events-none" style={style} title="Güvenli Baskı Alanı"></div>
                                } catch (e) { return null; }
                            })()}
                        </div>
                        <div className="p-3">
                            <h3 className="font-bold text-sm truncate">{t.name}</h3>
                            <p className="text-xs text-slate-500 truncate" title={t.path}>{t.path.split('/').pop()}</p>
                        </div>
                    </div>
                ))}

                {/* Upload Placeholder */}
                <div onClick={onUpload} className="aspect-[1/1.4] border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl flex flex-col items-center justify-center text-slate-400 cursor-pointer hover:border-primary hover:text-primary hover:bg-slate-50 transition-all">
                    <Plus size={40} className="mb-2" />
                    <span className="font-bold">Yeni Şablon</span>
                </div>
            </div>
        </motion.div>
    );
}
