import { useState, useEffect } from "react";
import { Margins } from "../types";
import { X, Save } from "lucide-react";

interface TemplateEditorModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (name: string, margins: Margins) => void;
    initialPreview: string;
    initialMargins: Margins;
    initialName?: string;
}

export default function TemplateEditorModal({
    isOpen, onClose, onSave, initialPreview, initialMargins, initialName
}: TemplateEditorModalProps) {
    const [name, setName] = useState(initialName || "Yeni Şablon");
    const [margins, setMargins] = useState<Margins>(initialMargins);

    useEffect(() => {
        if (isOpen) {
            setMargins(initialMargins);
            setName(initialName || "Yeni Şablon");
        }
    }, [isOpen, initialMargins, initialName]);

    if (!isOpen) return null;

    const handleSave = () => {
        if (!name.trim()) return alert("Lütfen bir isim girin.");
        if (margins.top >= margins.bottom) return alert("Üst kenar alt kenardan büyük olamaz.");
        if (margins.left >= margins.right) return alert("Sol kenar sağ kenardan büyük olamaz.");
        onSave(name, margins);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-4xl h-[90vh] flex overflow-hidden animate-in fade-in zoom-in duration-200">

                {/* Left: Preview with Overlay */}
                <div className="flex-1 bg-slate-100 dark:bg-black relative flex items-center justify-center p-4 overflow-hidden">
                    <div className="relative shadow-lg max-h-full aspect-[1/1.414]">
                        <img src={initialPreview} className="w-full h-full object-contain pointer-events-none select-none" />

                        {/* Overlay Box */}
                        <div
                            className="absolute border-2 border-emerald-500 bg-emerald-500/20 shadow-[0_0_0_9999px_rgba(0,0,0,0.5)]"
                            style={{
                                top: `${margins.top / 10}%`,
                                bottom: `${(1000 - margins.bottom) / 10}%`,
                                left: `${margins.left / 10}%`,
                                right: `${(1000 - margins.right) / 10}%`
                            }}
                        >
                            <div className="absolute top-0 left-0 bg-emerald-500 text-white text-[10px] px-1">Güvenli Alan</div>
                        </div>
                    </div>
                </div>

                {/* Right: Controls */}
                <div className="w-80 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 flex flex-col overflow-y-auto">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-lg">Şablon Düzenle</h3>
                        <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-lg"><X size={20} /></button>
                    </div>

                    <div className="space-y-6 flex-1">
                        <div>
                            <label className="block text-sm font-medium mb-2">Şablon İsmi</label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full p-2 border rounded-lg bg-transparent"
                            />
                        </div>

                        <hr className="border-slate-200 dark:border-slate-800" />

                        <div className="space-y-4">
                            <h4 className="font-bold text-sm text-slate-500 uppercase">Kenar Boşlukları</h4>

                            <Control
                                label="Üst Boşluk"
                                value={margins.top}
                                max={margins.bottom - 50}
                                onChange={v => setMargins({ ...margins, top: v })}
                            />
                            <Control
                                label="Alt Sınır"
                                value={margins.bottom}
                                min={margins.top + 50}
                                max={1000}
                                onChange={v => setMargins({ ...margins, bottom: v })}
                            />
                            <Control
                                label="Sol Boşluk"
                                value={margins.left}
                                max={margins.right - 50}
                                onChange={v => setMargins({ ...margins, left: v })}
                            />
                            <Control
                                label="Sağ Sınır"
                                value={margins.right}
                                min={margins.left + 50}
                                max={1000}
                                onChange={v => setMargins({ ...margins, right: v })}
                            />
                        </div>
                    </div>

                    <div className="mt-6">
                        <button
                            onClick={handleSave}
                            className="w-full py-3 bg-primary text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-primary/90 shadow-lg shadow-primary/20"
                        >
                            <Save size={18} />
                            Kaydet
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

interface ControlProps {
    label: string;
    value: number;
    min?: number;
    max?: number;
    onChange: (val: number) => void;
}

function Control({ label, value, min = 0, max = 1000, onChange }: ControlProps) {
    return (
        <div>
            <div className="flex justify-between mb-1">
                <label className="text-xs font-medium">{label}</label>
                <span className="text-xs font-mono bg-slate-100 px-1 rounded">{value}</span>
            </div>
            <input
                type="range"
                min={min}
                max={max}
                value={value}
                onChange={(e) => onChange(parseInt(e.target.value))}
                className="w-full accent-primary h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            />
        </div>
    )
}
