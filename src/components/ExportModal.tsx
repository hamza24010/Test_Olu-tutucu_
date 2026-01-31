import { Template } from "../types";
import { Layout, CheckCircle } from "lucide-react";

interface ExportModalProps {
    isOpen: boolean;
    onClose: () => void;
    onExport: (templateId: number | null) => void;
    templates: Template[];
    selectedCount: number;
    selectedTemplateId: number | null;
    setSelectedTemplateId: (id: number | null) => void;
}

export default function ExportModal({
    isOpen, onClose, onExport, templates, selectedCount, selectedTemplateId, setSelectedTemplateId
}: ExportModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
                <h3 className="text-xl font-bold mb-4">Test Oluştur</h3>
                <p className="text-slate-500 mb-6">Seçilen {selectedCount} soru ile PDF oluşturulacak. Bir şablon seçebilirsiniz.</p>

                <div className="space-y-3 mb-8 max-h-60 overflow-y-auto pr-2">
                    <label className="flex items-center gap-3 p-3 border rounded-xl cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700 transition">
                        <input type="radio" name="template" checked={selectedTemplateId === null} onChange={() => setSelectedTemplateId(null)} />
                        <div className="flex items-center gap-2">
                            <Layout size={18} />
                            <span className="font-medium">Standart Şablonsuz (Beyaz Sayfa)</span>
                        </div>
                    </label>

                    {templates.length > 0 && <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mt-2 sticky top-0 bg-white dark:bg-slate-800 py-1">Kayıtlı Şablonlarım</p>}

                    {templates.map(t => (
                        <label key={t.id} className="flex items-center gap-3 p-3 border rounded-xl cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700 transition relative overflow-hidden">
                            <input type="radio" name="template" checked={selectedTemplateId === t.id} onChange={() => setSelectedTemplateId(t.id)} />
                            <div className="w-10 h-14 bg-slate-200 rounded shrink-0 overflow-hidden border">
                                <img src={t.preview_image} className="w-full h-full object-cover" />
                            </div>
                            <span className="font-medium truncate flex-1">{t.name}</span>
                            {selectedTemplateId === t.id && <CheckCircle className="ml-auto text-primary" size={20} />}
                        </label>
                    ))}
                </div>

                <div className="flex gap-3">
                    <button onClick={onClose} className="flex-1 py-2 rounded-xl bg-slate-100 dark:bg-slate-700 font-medium hover:bg-slate-200 transition">İptal</button>
                    <button onClick={() => onExport(selectedTemplateId)} className="flex-1 py-2 rounded-xl bg-primary text-white font-medium hover:bg-primary/90 transition shadow-lg shadow-primary/20">Oluştur</button>
                </div>
            </div>
        </div>
    );
}
