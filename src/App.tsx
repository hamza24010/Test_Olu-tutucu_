import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open, save } from "@tauri-apps/plugin-dialog";
import { AnimatePresence } from "framer-motion";
import { Database, Upload, Scan, Bell, FileText, Trash2, Plus, Edit3 } from "lucide-react";

// Types
import { Question, Template, Margins } from "./types";

// Components
import Sidebar from "./components/Sidebar";
import ExportModal from "./components/ExportModal";
import TemplateEditorModal from "./components/TemplateEditorModal";

// Views
import LibraryView from "./components/views/LibraryView";
import TemplatesView from "./components/views/TemplatesView";
import UploadView from "./components/views/UploadView";
import CreateTestView from "./components/views/CreateTestView";
import StudentsView from "./components/views/StudentsView";
import ArchiveView from "./components/views/ArchiveView";
import SettingsView from "./components/views/SettingsView";


function App() {
  // Navigation State
  const [activeView, setActiveView] = useState<'upload' | 'analyze' | 'library' | 'templates' | 'create-test' | 'students' | 'archive' | 'settings'>('upload');

  // Data States
  const [questions, setQuestions] = useState<Question[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);

  // UI States
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("İşlem Yapılıyor...");
  const [analysisProgress, setAnalysisProgress] = useState<{ current: number, total: number }>({ current: 0, total: 0 });

  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<any[]>([]);

  // Editor State
  const [editorData, setEditorData] = useState<{
    isOpen: boolean,
    mode: 'new' | 'edit',
    id?: number,
    path: string,
    preview: string,
    margins: Margins,
    name?: string
  }>({ isOpen: false, mode: 'new', path: "", preview: "", margins: { top: 0, bottom: 0, left: 0, right: 0 } });

  // Export Modal State
  const [showExportModal, setShowExportModal] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  // NEW: Store questions specifically for export (if not from library selection)
  const [questionsToExport, setQuestionsToExport] = useState<Question[]>([]);
  const [exportStudentId, setExportStudentId] = useState<number | null>(null);

  useEffect(() => {
    // if (activeView === 'library') loadLibrary(); // Internalized
    if (activeView === 'templates') loadTemplates();
  }, [activeView]);

  // --- API Calls ---

  // loadLibrary removed as it is now inside LibraryView

  const loadTemplates = async () => {
    try {
      const res = await invoke<Template[]>('list_templates');
      setTemplates(res);
    } catch (e) { console.error(e); }
  }

  const handleDeleteQuestions = async (ids: any[]) => {
    if (!confirm(`${ids.length} soruyu silmek istediğinize emin misiniz?`)) return;
    try {
      await invoke('delete_questions', { ids });
      // LibraryView reloads itself via onDelete calback wrapper logic inside it?
      // Wait, LibraryView calls onDelete which is this function.
      // But this function updates nothing in App.tsx related to list now.
      // So LibraryView needs to trigger reload itself.
      // We can return success here.
      setSelectedIds([]);
    } catch (e) { alert("Silme hatası: " + e); }
  };

  const handleDeleteTemplate = async (id: number) => {
    if (!confirm("Şablonu silmek istediğinize emin misiniz?")) return;
    try {
      await invoke('delete_template', { id });
      loadTemplates();
    } catch (e) { alert("Silme hatası: " + e); }
  }

  const handleTemplateUpload = async () => {
    try {
      const selected = await open({ multiple: false, filters: [{ name: 'PDF Template', extensions: ['pdf'] }] });

      if (selected && typeof selected === 'string') {
        setLoading(true);
        setLoadingText("Şablon Analiz Ediliyor (Gemini)...");

        const resultStr = await invoke<string>('analyze_template', { path: selected });
        const result = JSON.parse(resultStr);
        if (result.error) throw new Error(result.error);

        setEditorData({
          isOpen: true,
          mode: 'new',
          path: selected,
          preview: result.preview_base64,
          margins: result.margins
        });
      }
    } catch (e: any) { alert("Şablon Hatası: " + e.message); }
    finally { setLoading(false); setLoadingText("İşlem Yapılıyor..."); }
  }

  const handleEditTemplate = (t: Template) => {
    try {
      const m = JSON.parse(t.margins_json);
      setEditorData({
        isOpen: true,
        mode: 'edit',
        id: t.id,
        path: t.path,
        preview: t.preview_image,
        margins: m,
        name: t.name
      });
    } catch (e) { alert("Hata: " + e); }
  }

  const handleEditorSave = async (name: string, margins: Margins) => {
    try {
      if (editorData.mode === 'new') {
        await invoke('save_template', {
          name,
          path: editorData.path,
          preview: editorData.preview,
          margins: JSON.stringify(margins)
        });
        alert("Şablon kaydedildi.");
      } else {
        await invoke('update_template', {
          id: editorData.id,
          name,
          margins: JSON.stringify(margins)
        });
        alert("Şablon güncellendi.");
      }
      loadTemplates();
    } catch (e: any) { alert("Kaydetme hatası: " + e); }
  }

  // Generic Export Starter
  const startExport = (questions: Question[], studentId: number | null = null) => {
    setQuestionsToExport(questions);
    setExportStudentId(studentId);
    loadTemplates();
    setShowExportModal(true);
  }

  // Triggered by Library
  const startLibraryExport = async () => {
    if (selectedIds.length === 0) return;

    setLoading(true);
    try {
      const questions = await invoke<Question[]>('get_questions_by_ids', { ids: selectedIds });
      startExport(questions, null); // Library export has no specific student context usually
    } catch (e) {
      alert("Soru getirme hatası: " + e);
    } finally {
      setLoading(false);
    }
  }

  const handleExport = async (templateId: number | null) => {
    setShowExportModal(false);

    const imagePaths = questionsToExport.map(q => q.image_path).filter(p => p) as string[];

    if (imagePaths.length === 0) { alert("Seçilen soruların dosyaları bulunamadı."); return; }

    try {
      let templatePath: string | null = null;
      let margins: string | null = null;

      if (templateId) {
        const tpl = templates.find(t => t.id === templateId);
        if (tpl) {
          templatePath = tpl.path;
          margins = tpl.margins_json;
        }
      }

      const filePath = await save({ filters: [{ name: 'PDF', extensions: ['pdf'] }], defaultPath: 'Deneme_Sinavi.pdf' });
      if (!filePath) return;

      setLoading(true);
      setLoadingText("PDF Oluşturuluyor...");
      setAnalysisProgress({ current: 0, total: 0 });

      await invoke('export_test_pdf', { imagePaths, outputPath: filePath, templatePath, margins });

      // NEW: Archive the test record
      const qIds = questionsToExport.map(q => q.id);
      await invoke('save_test_record', { studentId: exportStudentId, questionIds: qIds });

      // NEW: Mark as solved if student selected
      if (exportStudentId) {
        await invoke('mark_test_solved', { studentId: exportStudentId, questionIds: qIds });
        console.log(`Marked ${qIds.length} questions as solved for student ${exportStudentId}`);
      }

      alert("Test başarıyla oluşturuldu!\n" + filePath);

    } catch (e) { alert("Hata: " + e); }
    finally { setLoading(false); }
  };

  // --- STREAMING ANALYSIS ---
  const startAnalysis = async (filePath: string) => {
    setLoading(true);
    setLoadingText("PDF Hazırlanıyor...");
    setQuestions([]);
    setAnalysisProgress({ current: 0, total: 0 });
    setError(null);

    // Setup Listener
    const unlisten = await listen<string>("analysis-event", (event) => {
      try {
        const data = JSON.parse(event.payload);

        // Catch global errors from engine.py
        if (data.status === 'error' || data.type === 'error') {
          setError(data.message || data.error || "Beklenmeyen bir hata oluştu.");
          setLoading(false);
          return;
        }

        if (data.type === 'start') {
          setAnalysisProgress({ current: 0, total: data.total });
          setLoadingText("Analiz Başlıyor...");
        } else if (data.type === 'progress') {
          setAnalysisProgress(prev => ({ ...prev, current: data.current }));
          if (data.questions && data.questions.length > 0) {
            setQuestions(prev => [...prev, ...data.questions]);
          }
        } else if (data.type === 'finish') {
          setLoading(false);
          if (activeView !== 'analyze') setActiveView('analyze');
        } else if (data.type === 'error') {
          setError(data.message || "Bilinmeyen bir hata oluştu.");
          setLoading(false);
        }
      } catch (e) {
        console.error("AI Log:", event.payload);
      }
    });

    try {
      await invoke("analyze_pdf", { path: filePath });
    } catch (err: any) {
      setError("Başlatma hatası: " + err.message);
      setLoading(false);
      unlisten();
    }
  };

  const handleFileUpload = async () => {
    try {
      setError(null);
      const selected = await open({ multiple: false, filters: [{ name: 'PDF', extensions: ['pdf'] }] });
      if (selected && typeof selected === 'string') {
        setPdfPath(selected);
        startAnalysis(selected);
      }
    } catch (err: any) { setError("Dosya hatası: " + err.message); }
  };

  const handleSaveQuestion = async (q: Question) => {
    try {
      await invoke('save_question', {
        text: q.text, image: q.image_path || q.image, base64: q.image.startsWith('data:') ? q.image : "",
        pdf: pdfPath || "unknown.pdf", page: q.page, difficulty: q.difficulty || 3, topic: q.topic || "Genel"
      });
      alert("Kaydedildi");
    } catch (e) { alert("Hata: " + e); }
  };

  const handleSaveAllQuestions = async () => {
    if (!confirm("Tümünü kaydet?")) return;
    try {
      let count = 0;
      for (const q of questions) {
        await invoke('save_question', {
          text: q.text, image: q.image_path || q.image, base64: q.image.startsWith('data:') ? q.image : "",
          pdf: pdfPath || "unknown.pdf", page: q.page, difficulty: q.difficulty || 3, topic: q.topic || "Genel"
        });
        count++;
      }
      alert(`${count} soru kaydedildi.`);
    } catch (e) { alert("Hata: " + e); }
  };

  const toggleSelection = (id: any) => {
    if (selectedIds.includes(id)) setSelectedIds(selectedIds.filter(i => i !== id));
    else setSelectedIds([...selectedIds, id]);
  };

  // --- Render Helpers ---

  const getHeaderTitle = () => {
    if (activeView === 'library') return { icon: <Database className="text-primary" />, text: "Soru Bankası" };
    if (activeView === 'templates') return { icon: <Scan className="text-primary" />, text: "Şablon Yönetimi" };
    if (activeView === 'create-test') return { icon: <Edit3 className="text-primary" />, text: "Otomatik Test Oluşturucu" };
    return { icon: <Upload className="text-slate-400" />, text: pdfPath?.split('/').pop() || "PDF Yükleme Merkezi" };
  };

  const header = getHeaderTitle();

  return (
    <div className="flex h-screen bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 overflow-hidden font-sans">

      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExport}
        templates={templates}
        selectedCount={questionsToExport.length}
        selectedTemplateId={selectedTemplateId}
        setSelectedTemplateId={setSelectedTemplateId}
      />

      <TemplateEditorModal
        isOpen={editorData.isOpen}
        onClose={() => setEditorData({ ...editorData, isOpen: false })}
        onSave={handleEditorSave}
        initialPreview={editorData.preview}
        initialMargins={editorData.margins}
        initialName={editorData.name}
      />

      <Sidebar activeView={activeView} onViewChange={setActiveView} />

      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-10">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            {header.icon}
            <span className="truncate max-w-md">{header.text}</span>
          </h2>

          <div className="flex items-center gap-4">
            {activeView === 'library' && selectedIds.length > 0 && (
              <div className="flex items-center gap-4 bg-slate-100 px-4 py-1 rounded-full border border-slate-200">
                <span className="text-sm font-medium text-slate-600">{selectedIds.length} Seçildi</span>
                <button onClick={startLibraryExport} className="text-white bg-primary hover:bg-primary/90 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 transition-colors">
                  <FileText size={14} /> PDF Oluştur
                </button>
                <div className="w-px h-4 bg-slate-300 mx-1"></div>
                <button onClick={() => handleDeleteQuestions(selectedIds)} className="text-red-500 hover:bg-red-50 p-1.5 rounded-full"><Trash2 size={16} /></button>
              </div>
            )}

            {activeView === 'templates' && (
              <button onClick={handleTemplateUpload} className="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 hover:bg-slate-800 transition shadow-lg shadow-slate-900/20">
                <Plus size={16} /> Yeni Şablon
              </button>
            )}

            <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full relative">
              <Bell size={20} className="text-slate-500" />
            </button>
            <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700"></div>
          </div>
        </header>

        {/* Workspace */}
        <div className="flex-1 overflow-hidden relative p-6">
          <AnimatePresence mode="wait">

            {activeView === 'library' && (
              <LibraryView
                selectedIds={selectedIds}
                onToggleSelection={toggleSelection}
                onDelete={handleDeleteQuestions}
              />
            )}

            {activeView === 'templates' && (
              <TemplatesView
                templates={templates}
                onDelete={handleDeleteTemplate}
                onUpload={handleTemplateUpload}
                onEdit={handleEditTemplate}
              />
            )}

            {activeView === 'students' && (
              <StudentsView />
            )}

            {activeView === 'archive' && (
              <ArchiveView />
            )}

            {activeView === 'settings' && (
              <SettingsView />
            )}

            {activeView === 'create-test' && (
              <CreateTestView
                onExport={startExport}
              />
            )}

            {(activeView === 'upload' || activeView === 'analyze') && (
              <UploadView
                loading={loading}
                loadingText={loadingText}
                progress={analysisProgress}
                pdfPath={pdfPath}
                questions={questions}
                error={error}
                onUpload={handleFileUpload}
                onSaveQuestion={handleSaveQuestion}
                onSaveAll={handleSaveAllQuestions}
                onReset={() => { setQuestions([]); setActiveView('upload'); }}
              />
            )}

          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
