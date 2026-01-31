export const getDifficultyColor = (level?: number) => {
    if (!level) return "bg-gray-100 text-gray-600";
    if (level <= 2) return "bg-green-100 text-green-700";
    if (level === 3) return "bg-yellow-100 text-yellow-700";
    return "bg-red-100 text-red-700";
};

export const getDifficultyLabel = (level?: number) => {
    if (!level) return "Belirsiz";
    if (level <= 2) return "Kolay";
    if (level === 3) return "Orta";
    return "Zor";
};
