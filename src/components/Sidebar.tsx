import { Layout, Upload, Database, Scan, Settings, Edit3, GraduationCap, Archive } from "lucide-react";
import clsx from "clsx";

interface SidebarProps {
    activeView: string;
    onViewChange: (view: 'upload' | 'library' | 'templates' | 'create-test' | 'students' | 'archive') => void;
}

export default function Sidebar({ activeView, onViewChange }: SidebarProps) {
    return (
        <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-background-dark flex flex-col h-full shrink-0 z-20">
            <div className="p-6 flex items-center gap-3">
                <div className="bg-primary p-2 rounded-lg text-white shadow-lg shadow-primary/30">
                    <Layout size={24} />
                </div>
                <div>
                    <h1 className="text-xl font-bold leading-none tracking-tight">Docling</h1>
                    <p className="text-xs text-slate-500 font-medium mt-0.5">Soru Asistanı</p>
                </div>
            </div>

            <nav className="flex-1 px-4 space-y-1 mt-4">
                <NavItem
                    icon={<Upload size={20} />}
                    label="PDF Yükle"
                    active={activeView === 'upload' || activeView === 'analyze'}
                    onClick={() => onViewChange('upload')}
                />
                <NavItem
                    icon={<Database size={20} />}
                    label="Soru Bankası"
                    active={activeView === 'library'}
                    onClick={() => onViewChange('library')}
                />
                <NavItem
                    icon={<Edit3 size={20} />}
                    label="Otomatik Test"
                    active={activeView === 'create-test'}
                    onClick={() => onViewChange('create-test')}
                />
                <NavItem
                    icon={<GraduationCap size={20} />}
                    label="Öğrenciler"
                    active={activeView === 'students'}
                    onClick={() => onViewChange('students')}
                />
                <NavItem
                    icon={<Archive size={20} />}
                    label="Geçmiş Testler"
                    active={activeView === 'archive'}
                    onClick={() => onViewChange('archive')}
                />
                <NavItem
                    icon={<Scan size={20} />}
                    label="Şablonlarım"
                    active={activeView === 'templates'}
                    onClick={() => onViewChange('templates')}
                />
            </nav>

            <div className="p-4 border-t border-slate-100 dark:border-slate-800 space-y-1">
                <NavItem icon={<Settings size={20} />} label="Ayarlar" />
            </div>
        </aside>
    );
}

function NavItem({ icon, label, active = false, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={clsx(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                active
                    ? "bg-slate-900 text-white shadow-md shadow-slate-900/10 dark:bg-white dark:text-slate-900"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100"
            )}
        >
            {icon}
            <span>{label}</span>
        </button>
    )
}
