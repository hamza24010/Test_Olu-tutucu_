import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { ask, message } from "@tauri-apps/plugin-dialog";
import { motion } from "framer-motion";
import { Settings, Key, Save, CheckCircle2, AlertCircle, Trash2 } from "lucide-react";

export default function SettingsView() {
    const [apiKey, setApiKey] = useState("");
    const [aiEngine, setAiEngine] = useState("gemini");
    const [saving, setSaving] = useState(false);
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const key = await invoke<string | null>('get_setting', { key: 'gemini_api_key' });
            if (key) setApiKey(key);

            const engine = await invoke<string | null>('get_setting', { key: 'ai_engine' });
            if (engine) setAiEngine(engine);
        } catch (e) { console.error(e); }
    };

    const handleSave = async () => {
        setSaving(true);
        setStatus('idle');
        try {
            await invoke('save_setting', { key: 'gemini_api_key', value: apiKey });
            await invoke('save_setting', { key: 'ai_engine', value: aiEngine });
            setStatus('success');
            setTimeout(() => setStatus('idle'), 3000);
        } catch (e) {
            console.error(e);
            setStatus('error');
        } finally {
            setSaving(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto py-10"
        >
            <div className="flex items-center gap-3 mb-8">
                <div className="p-3 bg-primary/10 rounded-2xl text-primary">
                    <Settings size={24} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Ayarlar</h1>
                    <p className="text-slate-500 text-sm">Uygulama tercihlerini ve API anahtarlarını yönetin.</p>
                </div>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 dark:border-slate-700">
                    <h3 className="font-bold flex items-center gap-2 text-slate-700 dark:text-slate-200">
                        <Key size={18} className="text-primary" />
                        AI Servis Yapılandırması
                    </h3>
                </div>

                <div className="p-6 space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                            Varsayılan Motor
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            <button
                                onClick={() => setAiEngine('gemini')}
                                className={`p-4 rounded-xl border-2 text-left transition-all relative ${aiEngine === 'gemini'
                                    ? 'border-primary bg-primary/5 shadow-md'
                                    : 'border-slate-200 dark:border-slate-700 hover:border-primary/50'
                                    }`}
                            >
                                <div className="font-bold text-slate-800 dark:text-white mb-1">Google Gemini 2.5</div>
                                <div className="text-xs text-slate-500">Tam OCR + Anlamlandırma. İnternet gerekir.</div>
                                {aiEngine === 'gemini' && <div className="absolute top-3 right-3 text-primary"><CheckCircle2 size={18} /></div>}
                            </button>

                            <button
                                onClick={() => setAiEngine('yolo')}
                                className={`p-4 rounded-xl border-2 text-left transition-all relative ${aiEngine === 'yolo'
                                    ? 'border-primary bg-primary/5 shadow-md'
                                    : 'border-slate-200 dark:border-slate-700 hover:border-primary/50'
                                    }`}
                            >
                                <div className="font-bold text-slate-800 dark:text-white mb-1">YOLOv26 (Yerel - Özel Eğitim)</div>
                                <div className="text-xs text-slate-500">Sadece Görsel Kesme. Hızlı & Çevrimdışı.</div>
                                {aiEngine === 'yolo' && <div className="absolute top-3 right-3 text-primary"><CheckCircle2 size={18} /></div>}
                            </button>
                        </div>

                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Gemini API Key
                        </label>
                        <div className={`relative transition-opacity ${aiEngine === 'yolo' ? 'opacity-50 pointer-events-none' : ''}`}>

                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder="ghp_... veya API anahtarınız"
                                className="w-full pl-4 pr-12 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none text-slate-700 dark:text-slate-200"
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                                <Key size={18} />
                            </div>
                        </div>
                        <p className="mt-2 text-xs text-slate-500">
                            Soruları analiz etmek ve çözmek için Google Gemini API anahtarı gereklidir.
                            <a href="https://aistudio.google.com/app/apikey" target="_blank" className="text-primary hover:underline ml-1">Buradan ücretsiz alabilirsiniz.</a>
                        </p>
                    </div>

                    <div className="pt-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            {status === 'success' && (
                                <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-emerald-500 text-sm flex items-center gap-1 font-medium">
                                    <CheckCircle2 size={16} /> Ayarlar kaydedildi
                                </motion.span>
                            )}
                            {status === 'error' && (
                                <span className="text-red-500 text-sm flex items-center gap-1 font-medium">
                                    <AlertCircle size={16} /> Hata oluştu
                                </span >
                            )}
                        </div>

                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="bg-primary hover:bg-primary-dark text-white px-6 py-2.5 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-primary/20 disabled:opacity-50"
                        >
                            {saving ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <Save size={18} />
                            )}
                            Değişiklikleri Kaydet
                        </button>
                    </div>
                </div>
            </div>

            <div className="mt-8 bg-red-50 dark:bg-red-900/10 rounded-3xl border border-red-200 dark:border-red-900/30 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-red-100 dark:border-red-900/30">
                    <h3 className="font-bold flex items-center gap-2 text-red-700 dark:text-red-400">
                        <AlertCircle size={18} />
                        Tehlikeli Bölge
                    </h3>
                </div>
                <div className="p-6 flex items-center justify-between">
                    <div>
                        <h4 className="font-bold text-slate-800 dark:text-white text-sm">Tüm Soru Bankasını Temizle</h4>
                        <p className="text-xs text-slate-500 mt-1 max-w-sm">
                            Veritabanındaki tüm sorular kalıcı olarak silinecektir. Bu işlem geri alınamaz.
                        </p>
                    </div>
                    <button
                        onClick={async () => {
                            const confirmed = await ask('Tüm soru bankasını silmek istediğinize emin misiniz? Bu işlem geri alınamaz.', {
                                title: 'Dikkat!',
                                kind: 'warning',
                            });

                            if (confirmed) {
                                try {
                                    await invoke('clear_database');
                                    await message('Veritabanı başarıyla temizlendi.', { title: 'Başarılı', kind: 'info' });
                                } catch (error) {
                                    await message(`Hata: ${error}`, { title: 'Hata', kind: 'error' });
                                }
                            }
                        }}
                        className="bg-red-50 text-red-600 hover:bg-red-600 hover:text-white border border-red-200 hover:border-red-600 px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2"
                    >
                        <Trash2 size={16} />
                        Tümünü Sil
                    </button>
                </div>
            </div>

            <div className="mt-8 p-6 bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-900/30 rounded-2xl">
                <h4 className="text-amber-800 dark:text-amber-400 font-bold text-sm mb-1 flex items-center gap-2">
                    <AlertCircle size={16} /> Önemli Bilgi
                </h4>
                <p className="text-amber-700 dark:text-amber-500 text-xs leading-relaxed">
                    API anahtarınız yerel veritabanında güvenli bir şekilde saklanır.
                    Uygulamanın PDF'leri doğru bir şekilde okuyabilmesi için geçerli ve kotalı bir anahtar kullandığınızdan emin olun.
                </p>
            </div>
        </motion.div>
    );
}
