from .google_ai import (
    GoogleAI_TextNode, PMS_GeminiChat,
    GoogleAI_TextVisionNode, GoogleAI_NanoBananaNode, PMS_NanaBanana,
    GoogleAI_ImageNode, GoogleAI_VideoGenerator, GoogleAI_VideoInterpolation,
    GoogleAI_VideoStoryboard, GoogleAI_ModelArchitectureDetector,
    GoogleAI_TriggerWordExtractor, GoogleAI_WorkflowAnalyzer,
    GoogleAI_CompatibilityChecker, GoogleAI_LoRATrainingAnalyzer, PMS_GeminiTTS,
)
from .grok_ai import (
    GrokTextNode, PMS_GrokImageGen, PMS_GrokVideoGen, PMS_GrokTTS, PMS_GrokSTT,
)
from .getset_pro import (
    PRO_SetNode, PRO_GetNode, PRO_UnetLoaderGGUF, PRO_SetNodeNamed,
    PRO_UnetLoaderGGUFAdvanced, PRO_ListCacheNode, PRO_ClearCacheNode,
)
from .selectores import (
    SelectorDeImagenes, SelectorDePrompts, ImagenLatentePro, PromptPro,
)
from .batch import PMS_DualPromptListBatch, PMS_VideoBatchConcat
from .frame import GetLastFrame, GetFrameByIndex
from .blocker import TextPromptBlocker, TextPromptBlockerPreview
from .divisor import DivisorDePrompts

ALL_LEGACY_NODES = [
    GoogleAI_TextNode, PMS_GeminiChat,
    GoogleAI_TextVisionNode, GoogleAI_NanoBananaNode, PMS_NanaBanana,
    GoogleAI_ImageNode, GoogleAI_VideoGenerator, GoogleAI_VideoInterpolation,
    GoogleAI_VideoStoryboard, GoogleAI_ModelArchitectureDetector,
    GoogleAI_TriggerWordExtractor, GoogleAI_WorkflowAnalyzer,
    GoogleAI_CompatibilityChecker, GoogleAI_LoRATrainingAnalyzer, PMS_GeminiTTS,
    GrokTextNode, PMS_GrokImageGen, PMS_GrokVideoGen, PMS_GrokTTS, PMS_GrokSTT,
    PRO_SetNode, PRO_GetNode, PRO_UnetLoaderGGUF, PRO_SetNodeNamed,
    PRO_UnetLoaderGGUFAdvanced, PRO_ListCacheNode, PRO_ClearCacheNode,
    SelectorDeImagenes, SelectorDePrompts, ImagenLatentePro, PromptPro,
    PMS_DualPromptListBatch, PMS_VideoBatchConcat,
    GetLastFrame, GetFrameByIndex,
    TextPromptBlocker, TextPromptBlockerPreview,
    DivisorDePrompts,
]
