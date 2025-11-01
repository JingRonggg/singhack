from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import os
import base64
from PIL import Image
from PIL.ExifTags import TAGS
import hashlib
import numpy as np
from datetime import datetime
from backend.util.config import load_config


class ImageAnalysisResult(BaseModel):
    """Schema for image analysis results."""

    authenticity_score: float = Field(
        description="Overall authenticity score (0-100, higher is more authentic)",
        ge=0,
        le=100,
    )
    is_ai_generated: bool = Field(
        description="Whether the image appears to be AI-generated"
    )
    ai_confidence: float = Field(
        description="Confidence level for AI detection (0-100)", ge=0, le=100
    )
    is_tampered: bool = Field(description="Whether the image shows signs of tampering")
    tampering_indicators: List[str] = Field(
        description="List of tampering indicators found"
    )
    metadata_analysis: Dict[str, str] = Field(description="Analysis of image metadata")
    forensic_findings: List[str] = Field(
        description="Detailed forensic analysis findings"
    )
    reverse_search_results: Optional[Dict[str, str]] = Field(
        description="Results from reverse image search if available"
    )
    recommendations: List[str] = Field(
        description="Recommendations based on the analysis"
    )
    timestamp: str = Field(description="Analysis timestamp")


def extract_image_metadata(image_path: str) -> Dict[str, str]:
    """
    Extracts EXIF and other metadata from an image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        Dict[str, str]: Dictionary containing metadata information.
    """
    metadata = {}

    try:
        with Image.open(image_path) as image:
            # Basic image info
            metadata["format"] = str(image.format)
            metadata["mode"] = str(image.mode)
            metadata["size"] = f"{image.size[0]}x{image.size[1]}"

            # Extract EXIF data
            exif_data = image._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[str(tag)] = str(value)
            else:
                metadata["exif_note"] = "No EXIF data found"

            # Check for common manipulation indicators in metadata
            metadata["has_editing_software"] = str(
                any(
                    key in metadata
                    for key in ["Software", "ProcessingSoftware", "CreatorTool"]
                )
            )

    except Exception as e:
        metadata["error"] = f"Failed to extract metadata: {str(e)}"

    return metadata


def analyze_pixel_anomalies(image_path: str) -> List[str]:
    """
    Analyzes pixel-level data for anomalies that may indicate tampering.

    Args:
        image_path (str): Path to the image file.

    Returns:
        List[str]: List of detected anomalies.
    """
    anomalies = []

    try:
        with Image.open(image_path) as image:
            img_format = image.format
            img_array = np.array(image.convert("RGB"))

        # Check for compression artifacts (JPEG ghosts)
        if img_format == "JPEG":
            # Calculate noise inconsistencies
            gray = np.mean(img_array, axis=2)
            noise_variance = np.var(gray)

            if noise_variance < 10:
                anomalies.append(
                    "Unusually low noise variance - possible heavy editing"
                )
            elif noise_variance > 5000:
                anomalies.append("High noise variance - possible composite image")

        # Check for statistical anomalies in color distribution
        for i, channel in enumerate(["Red", "Green", "Blue"]):
            channel_data = img_array[:, :, i]
            hist, _ = np.histogram(channel_data, bins=256, range=(0, 256))

            # Check for unnatural histogram patterns
            if np.max(hist) > channel_data.size * 0.3:
                anomalies.append(f"{channel} channel shows unnatural concentration")

        # Check for edge inconsistencies
        from scipy import ndimage

        edges = ndimage.sobel(np.mean(img_array, axis=2))
        edge_variance = np.var(edges)

        if edge_variance > 1000:
            anomalies.append("Inconsistent edge patterns detected")

        # Check for cloning patterns
        if len(img_array.shape) == 3:
            h, w, _ = img_array.shape
            if h > 100 and w > 100:
                # Simple correlation check for repeated patterns
                sample_size = min(50, h // 4, w // 4)
                region1 = img_array[0:sample_size, 0:sample_size]
                region2 = img_array[-sample_size:, -sample_size:]

                correlation = np.corrcoef(region1.flatten(), region2.flatten())[0, 1]
                if correlation > 0.95:
                    anomalies.append(
                        "High correlation between distant regions - possible cloning"
                    )

    except Exception as e:
        anomalies.append(f"Pixel analysis error: {str(e)}")

    return anomalies


def perform_reverse_image_search(image_path: str) -> Dict[str, str]:
    """
    Performs reverse image search to detect stolen or widely distributed images.

    Args:
        image_path (str): Path to the image file.

    Returns:
        Dict[str, str]: Results from reverse image search.
    """
    results = {}

    try:
        # Generate image hash for comparison
        with open(image_path, "rb") as f:
            image_data = f.read()
            image_hash = hashlib.sha256(image_data).hexdigest()

        results["image_hash"] = image_hash
        results["hash_algorithm"] = "SHA-256"

        # Note: In production, integrate with actual reverse image search APIs
        # such as Google Vision API, TinEye API, or similar services
        results["note"] = (
            "Reverse image search requires API integration (Google Vision, TinEye, etc.)"
        )
        results["recommendation"] = (
            "Manually verify image uniqueness using Google Images or TinEye"
        )

        # Perceptual hash for near-duplicate detection
        with Image.open(image_path) as image:
            small_image = image.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
            pixels = np.array(small_image).flatten()

        avg = pixels.mean()
        perceptual_hash = "".join(["1" if pixel > avg else "0" for pixel in pixels])

        results["perceptual_hash"] = perceptual_hash
        results["duplicate_detection"] = (
            "Use perceptual hash for near-duplicate matching"
        )

    except Exception as e:
        results["error"] = f"Reverse search failed: {str(e)}"

    return results


def detect_ai_mockup_heuristics(
    image_path: str, metadata: Dict[str, str]
) -> Dict[str, any]:
    """
    Applies heuristic checks to detect AI-generated UI mockups and screenshots.

    Args:
        image_path (str): Path to the image file.
        metadata (Dict[str, str]): Image metadata.

    Returns:
        Dict containing AI mockup detection results.
    """
    indicators = []
    ai_score = 0

    # Check 1: Missing camera/device EXIF data (real screenshots have this)
    has_camera_info = any(key in metadata for key in ["Make", "Model", "Software"])
    has_exif = (
        "exif_note" not in metadata or metadata.get("exif_note") != "No EXIF data found"
    )

    if not has_camera_info and not has_exif:
        indicators.append(
            "Missing EXIF/device metadata - not from real device screenshot"
        )
        ai_score += 30

    # Check 2: Image format - PNGs are common for mockups, real screenshots often JPEG
    image_format = metadata.get("format", "").upper()
    if image_format == "PNG":
        indicators.append("PNG format common for AI-generated UI mockups")
        ai_score += 10

    # Check 3: Check for overly clean edges (mockups vs. real screenshots)
    try:
        with Image.open(image_path) as image:
            img_array = np.array(image.convert("RGB"))

            # Check background uniformity (mockups often have solid backgrounds)
            # Sample corners to see if background is too uniform
            h, w = img_array.shape[:2]
            corner_size = min(50, h // 10, w // 10)

            corners = [
                img_array[0:corner_size, 0:corner_size],
                img_array[0:corner_size, -corner_size:],
                img_array[-corner_size:, 0:corner_size],
                img_array[-corner_size:, -corner_size:],
            ]

            corner_variances = [np.var(corner) for corner in corners]
            avg_corner_variance = np.mean(corner_variances)

            # Real screenshots have more texture/noise, mockups are cleaner
            if avg_corner_variance < 100:
                indicators.append(
                    "Suspiciously uniform background - typical of UI mockups"
                )
                ai_score += 20

            # Check 4: Color distribution - mockups often have limited, perfect colors
            for i, channel in enumerate(["Red", "Green", "Blue"]):
                channel_data = img_array[:, :, i]
                unique_colors = len(np.unique(channel_data))

                # Mockups often have fewer unique colors (flat design)
                if unique_colors < 50:
                    indicators.append(
                        f"{channel} channel has very few unique values - flat design typical of mockups"
                    )
                    ai_score += 15
                    break

    except Exception as e:
        indicators.append(f"Heuristic analysis error: {str(e)}")

    # Check 5: Aspect ratio - common mockup dimensions
    size_str = metadata.get("size", "")
    if "x" in size_str:
        try:
            width, height = map(int, size_str.split("x"))
            aspect_ratio = width / height if height > 0 else 0

            # Common mockup ratios: 9:16 (phone), perfect squares, or very standard dimensions
            common_mockup_ratios = [0.5625, 1.0, 0.75, 1.777]  # 9:16, 1:1, 3:4, 16:9

            for ratio in common_mockup_ratios:
                if abs(aspect_ratio - ratio) < 0.01:
                    indicators.append(
                        f"Perfect aspect ratio ({aspect_ratio:.2f}) typical of design mockups"
                    )
                    ai_score += 5
                    break
        except Exception:
            pass

    return {
        "ai_mockup_score": min(ai_score, 100),
        "indicators": indicators,
        "is_likely_mockup": ai_score >= 40,
    }


def encode_image_to_base64(image_path: str) -> str:
    """
    Encodes an image to base64 for API transmission.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded image string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image_with_llm(
    image_path: str,
    metadata: Dict[str, str],
    pixel_anomalies: List[str],
    reverse_search: Dict[str, str],
    mockup_detection: Dict[str, any] = None,
) -> ImageAnalysisResult:
    """
    Uses language model to perform comprehensive image analysis.

    Args:
        image_path (str): Path to the image file.
        metadata (Dict[str, str]): Extracted image metadata.
        pixel_anomalies (List[str]): Detected pixel-level anomalies.
        reverse_search (Dict[str, str]): Reverse image search results.

    Returns:
        ImageAnalysisResult: Comprehensive analysis results.
    """
    config = load_config()
    api_key = config.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")

    # Use Llama 3.2 Vision model which has better vision capabilities
    llm = ChatGroq(
        model="llama-3.2-90b-vision-preview",
        api_key=api_key,
        temperature=0.1,  # Lower temperature for more consistent detection
    )

    # Prepare image for analysis
    try:
        # Get image info
        with Image.open(image_path) as image:
            image_format = image.format
            image_size = image.size

        # Encode image for vision model
        base64_image = encode_image_to_base64(image_path)

    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")

    system_message = SystemMessage(
        content="""
        You are an advanced image forensics expert specializing in:
1. Authenticity verification and fraud detection
2. AI-generated image detection (Stable Diffusion, DALL-E, Midjourney, etc.)
3. Digital tampering and manipulation detection
4. Forensic analysis and metadata evaluation

**REAL vs FAKE IMAGE DETECTION CRITERIA:**

REAL IMAGES typically have:
- Natural noise patterns and compression artifacts consistent throughout
- EXIF metadata with camera make/model, GPS, and timestamp
- Realistic lighting physics (shadows match light sources, proper color temperature)
- Natural imperfections (slight blur, chromatic aberration, lens distortion)
- Consistent depth of field and focus gradients
- Organic textures with random variations
- Proper perspective and geometric accuracy
- Film grain or sensor noise patterns
- Metadata showing original capture device

**FAKE/AI-GENERATED IMAGES often show:
- Overly smooth or perfect textures (especially skin, hair, fabric)
- Unnatural symmetry or repetitive patterns
- Impossible reflections or shadows (direction/intensity mismatch)
- Anatomical errors (wrong finger count, distorted limbs, asymmetric faces)
- Text/letters that are gibberish or malformed
- Objects that blend unnaturally or have unclear boundaries
- Unrealistic bokeh or depth effects
- Missing or fabricated EXIF data
- Uniform lighting without natural variations
- "Too perfect" compositions or color grading
- Artifacts at edges or where objects meet
- Unnatural hair/fur textures (often too smooth or stringy)

**AI-GENERATED UI/MOCKUP/SCREENSHOT INDICATORS:**
- Generic placeholder names (e.g., "Emily Johnson", "John Doe") - very common in AI mockups
- Suspiciously round, clean numbers (e.g., exactly $500.00, $1000.00)
- Overly simplified, perfect UI design without real-world branding complexity
- Generic icons that lack authentic brand styling (basic shapes, simple colors)
- Perfect spacing and alignment - too clean for real screenshots
- Missing authentic app chrome/navigation that real banking apps have
- No status bar, battery, signal indicators if claiming to be phone screenshot
- Font rendering that's too perfect - lacks antialiasing artifacts from real screens
- Colors that are too vibrant/saturated compared to real banking apps
- Missing security elements (padlock icons, encryption indicators) real banks include
- Account numbers with obvious patterns or partial masking that looks artificial
- Date/time formats that don't match regional standards
- Lack of minor UI imperfections (slight misalignments, compression artifacts from real screenshots)

**STOLEN IMAGE DETECTION INDICATORS:**
- Watermark removal traces (blurred areas, cloning patterns)
- Mismatched metadata (creation date vs. content, wrong location)
- Low resolution suggesting multiple re-compressions
- Cropping that cuts off watermarks or signatures
- Inconsistent quality between different regions
- Signs of screenshot capture (compression artifacts, resolution)
- Hash matches or perceptual similarity to known sources

**TAMPERING DETECTION SPECIFICS:**
- Localized compression levels (JPEG ghosts)
- Color/lighting discontinuities at splice points
- Cloning patterns (repeated textures, copy-stamp artifacts)
- Edge inconsistencies (halos, sharp transitions)
- Noise variance differences between regions
- Shadow/reflection inconsistencies with added/removed objects
- Perspective mismatches in composite images
- Scale/proportion errors in manipulated elements

Analyze images comprehensively and provide detailed, actionable findings.
Be thorough but concise in your assessments.

You MUST respond with ONLY a valid JSON object that matches this exact schema:
{
    "authenticity_score": <number between 0-100>,
    "is_ai_generated": <boolean true or false>,
    "ai_confidence": <number between 0-100>,
    "is_tampered": <boolean true or false>,
    "tampering_indicators": [<array of strings>],
    "metadata_analysis": {<object with string keys and values>},
    "forensic_findings": [<array of strings>],
    "reverse_search_results": {<object with string keys and values or null>},
    "recommendations": [<array of strings>]
}

CRITICAL: Use actual numbers (not quoted strings) for scores and actual booleans (true/false, not "true"/"false") in the JSON."""
    )

    human_message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"""Perform a comprehensive forensic analysis of this image:

**Image Information:**
- Format: {image_format}
- Dimensions: {image_size[0]}x{image_size[1]}

**Metadata Analysis:**
{chr(10).join([f"- {k}: {v}" for k, v in list(metadata.items())[:20]])}

**Pixel-Level Anomalies Detected:**
{chr(10).join([f"- {anomaly}" for anomaly in pixel_anomalies]) if pixel_anomalies else "- No significant anomalies detected"}

**Reverse Image Search Info:**
{chr(10).join([f"- {k}: {v}" for k, v in reverse_search.items()])}

**AI Mockup Detection (Heuristics):**
{chr(10).join([f"- {indicator}" for indicator in mockup_detection.get('indicators', [])]) if mockup_detection else "- No heuristic analysis performed"}
- Mockup Score: {mockup_detection.get('ai_mockup_score', 0) if mockup_detection else 0}/100
- Likely AI Mockup: {mockup_detection.get('is_likely_mockup', False) if mockup_detection else False}

**Analysis Tasks:**

1. **Authenticity Verification (REAL vs FAKE):**
   - Score: 80-100 = Highly likely real, 50-79 = Uncertain/requires review, 0-49 = Likely fake/manipulated
   - Check for natural camera artifacts (lens distortion, chromatic aberration, sensor noise)
   - Verify lighting physics: Do shadows match light source direction? Is color temperature consistent?
   - Look for organic imperfections vs. AI's "too perfect" smoothness
   - Examine EXIF data: Does it match the image content? Are camera settings realistic?
   - RED FLAGS for fake: Perfect symmetry, unnatural smoothness, missing metadata, anatomical errors

2. **Stolen Image Detection:**
   - Check metadata for inconsistencies (timestamp vs. content, wrong geolocation)
   - Look for watermark removal artifacts (blurred patches, cloning patterns in corners/edges)
   - Assess image quality: Multiple re-compressions suggest reposting
   - Check for cropping patterns that might remove attribution
   - Examine compression artifacts suggesting screenshot or download
   - Note perceptual hash results for duplicate detection

3. **AI-Generated Detection:**
   - Confidence: 80-100 = Very likely AI, 50-79 = Possibly AI, 0-49 = Likely not AI
   - **FOR PHOTOS/IMAGES:**
     * Hands/fingers: Count digits, check joint positions, look for melting/merging
     * Text: Are letters readable or gibberish? Font consistency?
     * Textures: Hair too smooth? Fabric lacks weave pattern? Skin too perfect?
     * Eyes: Unnatural reflections? Asymmetric pupils? Wrong catchlight positions?
     * Backgrounds: Repetitive patterns? Objects that don't make sense?
     * Edges: Where subjects meet background - natural or blended?
   - **FOR UI/SCREENSHOTS/DOCUMENTS (CRITICAL FOR BANK TRANSACTIONS):**
     * Names: Generic placeholders like "Emily Johnson", "John Smith"? Flag as AI mockup
     * Numbers: Suspiciously round amounts ($500.00, $1000.00)? Too convenient = AI
     * Branding: Missing authentic bank logos, watermarks, security features?
     * UI Design: Too perfect/clean? Real apps have minor imperfections
     * Icons: Generic shapes vs authentic brand-specific icons?
     * Metadata: Screenshots from real phones have camera/device info - check EXIF
     * Typography: Too perfect rendering? Real screenshots have screen artifacts
     * Context: Does this look like a mockup/demo rather than real transaction?
     * Account numbers: Realistic patterns or obvious placeholders?
   - Check for model-specific tells: Midjourney's dreamy quality, DALL-E's distinct style, Stable Diffusion's artifacts
   - **CRITICAL: If this is a financial document/transaction, apply MAXIMUM scrutiny to realism**

4. **Tampering Detection:**
   - Look for JPEG ghosts (regions with different compression levels)
   - Detect cloning patterns: Repeated textures using same brush/stamp
   - Check lighting continuity: Do added objects match ambient lighting?
   - Examine shadows/reflections: Do they match physics of the scene?
   - Look for edge halos or unnatural transitions
   - Check noise patterns: Uniform across image or varies by region?
   - Detect perspective mismatches in composite images

5. **Forensic Analysis:**
   - Document EVERY specific finding with location in image
   - Prioritize findings by severity and confidence
   - Note: "Top-left corner shows [specific detail]", "Face region exhibits [specific artifact]"
   - Distinguish between CERTAIN indicators vs. POSSIBLE indicators
   - Consider compression/quality as confounding factors

6. **Risk Assessment & Recommendations:**
   - HIGH RISK: Multiple indicators of fake/stolen, suggest rejection
   - MEDIUM RISK: Some concerns, recommend manual review + additional verification
   - LOW RISK: Appears authentic, but note any minor concerns
   - Provide actionable steps: "Verify with document issuer", "Request higher resolution", etc.

**CRITICAL ANALYSIS PRINCIPLES:**
- Be SPECIFIC: Don't say "unnatural", say "left hand has 6 fingers"
- Provide EVIDENCE: Point to exact regions and observable features
- Consider CONTEXT: Low-quality photos may have artifacts that aren't manipulation
- Balance SENSITIVITY: Flag real concerns without false positives
- Quantify CONFIDENCE: Use score ranges meaningfully

**IMPORTANT TYPE REQUIREMENTS:**
- authenticity_score: Must be a NUMBER (0-100), not a string
- ai_confidence: Must be a NUMBER (0-100), not a string
- is_ai_generated: Must be a BOOLEAN (true/false), not a string
- is_tampered: Must be a BOOLEAN (true/false), not a string""",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )

    try:
        response = llm.invoke([system_message, human_message])

        # Parse the JSON response
        import json

        response_content = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Try to parse as JSON
        try:
            response_dict = json.loads(response_content)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from the response
            import re

            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                response_dict = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from response")

        # Helper function to safely convert to float
        def safe_float(value, default=50.0):
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            return default

        # Helper function to safely convert to bool
        def safe_bool(value, default=False):
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ["true", "1", "yes"]
            if isinstance(value, (int, float)):
                return bool(value)
            return default

        # Extract scores from LLM
        llm_ai_confidence = safe_float(response_dict.get("ai_confidence"), 0.0)
        llm_is_ai = safe_bool(response_dict.get("is_ai_generated"), False)

        # Combine heuristic and LLM results for better accuracy
        if mockup_detection:
            mockup_score = mockup_detection.get("ai_mockup_score", 0)
            # If heuristics strongly suggest mockup, boost confidence
            if mockup_score >= 40:
                llm_ai_confidence = max(llm_ai_confidence, mockup_score)
                llm_is_ai = True if mockup_score >= 60 else llm_is_ai

        # Create properly typed result
        result = ImageAnalysisResult(
            authenticity_score=safe_float(
                response_dict.get("authenticity_score"), 50.0
            ),
            is_ai_generated=llm_is_ai,
            ai_confidence=llm_ai_confidence,
            is_tampered=safe_bool(response_dict.get("is_tampered"), False),
            tampering_indicators=response_dict.get("tampering_indicators", []),
            metadata_analysis=response_dict.get("metadata_analysis", metadata),
            forensic_findings=response_dict.get("forensic_findings", []),
            reverse_search_results=response_dict.get("reverse_search_results"),
            recommendations=response_dict.get("recommendations", []),
            timestamp=datetime.now().isoformat(),
        )

        return result

    except Exception as e:
        # Return a fallback result if LLM fails
        return ImageAnalysisResult(
            authenticity_score=50.0,
            is_ai_generated=False,
            ai_confidence=0.0,
            is_tampered=len(pixel_anomalies) > 0,
            tampering_indicators=pixel_anomalies,
            metadata_analysis=metadata,
            forensic_findings=[f"Analysis error: {str(e)}"],
            reverse_search_results=reverse_search,
            recommendations=["Manual review required due to analysis error"],
            timestamp=datetime.now().isoformat(),
        )


@tool
def image_analysis(image_path: str) -> Dict:
    """
    A comprehensive tool that analyzes images for authenticity, AI-generation, tampering, and performs forensic analysis.

    Features:
    - Authenticity verification: Detect stolen images using reverse image search
    - AI-generated detection: Identify AI-generated or synthetic images
    - Tampering detection: Analyze metadata and pixel-level anomalies
    - Forensic analysis: Deep inspection for manipulation indicators

    Args:
        image_path (str): Path to the image file to analyze.

    Returns:
        Dict: Comprehensive analysis results including authenticity scores,
              AI detection, tampering indicators, and forensic findings.
    """

    if not os.path.exists(image_path):
        return {
            "error": f"Image file not found: {image_path}",
            "timestamp": datetime.now().isoformat(),
        }

    # Step 1: Extract metadata
    print(f"Extracting metadata from {image_path}...")
    metadata = extract_image_metadata(image_path)

    # Step 2: Analyze pixel-level anomalies
    print("Analyzing pixel-level anomalies...")
    pixel_anomalies = analyze_pixel_anomalies(image_path)

    # Step 3: Perform reverse image search
    print("Performing reverse image search analysis...")
    reverse_search = perform_reverse_image_search(image_path)

    # Step 4: AI mockup heuristic detection
    print("Checking for AI-generated mockup indicators...")
    mockup_detection = detect_ai_mockup_heuristics(image_path, metadata)

    # Step 5: Comprehensive LLM analysis
    print("Performing AI-powered forensic analysis...")
    analysis_result = analyze_image_with_llm(
        image_path, metadata, pixel_anomalies, reverse_search, mockup_detection
    )

    # Convert to dictionary for return
    result = analysis_result.dict()

    print("Analysis complete!")
    print(f"Authenticity Score: {result['authenticity_score']}/100")
    print(
        f"AI-Generated: {result['is_ai_generated']} (Confidence: {result['ai_confidence']}%)"
    )
    print(f"Tampering Detected: {result['is_tampered']}")

    return result


# Helper function for batch analysis
def batch_image_analysis(image_paths: List[str]) -> Dict[str, Dict]:
    """
    Analyzes multiple images in batch.

    Args:
        image_paths (List[str]): List of image paths to analyze.

    Returns:
        Dict[str, Dict]: Dictionary mapping each image path to its analysis results.
    """
    results = {}

    for image_path in image_paths:
        print(f"\n{'='*60}")
        print(f"Analyzing: {image_path}")
        print(f"{'='*60}")

        try:
            results[image_path] = image_analysis.invoke({"image_path": image_path})
        except Exception as e:
            results[image_path] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    return results
