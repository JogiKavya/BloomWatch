import React, { useRef, useState } from "react";
import { createRoot } from "react-dom/client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  CloudSun,
  FlaskConical,
  ImagePlus,
  Info,
  Leaf,
  LoaderCircle,
  ShieldAlert,
  Upload,
  Waves,
  X,
} from "lucide-react";

import "./styles.css";

const API =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const fields = [
  ["temperature", "Temperature"],
  ["ph", "pH"],
  ["dissolved_oxygen", "Dissolved oxygen"],
  ["salinity", "Salinity"],
  ["turbidity", "Turbidity"],
  ["chlorophyll", "Chlorophyll"],
  ["nitrate", "Nitrate"],
];

/* =========================================================
   RESULT COMPONENT
   ========================================================= */

function Result({ result, mode }) {
  const image =
    mode === "both"
      ? result?.image_assessment
      : mode === "image"
      ? result
      : null;

  const manual =
    mode === "both"
      ? result?.manual_assessment
      : mode === "manual"
      ? result
      : null;

  const unsupported =
    manual && manual.available === false;

  return (
    <div className="result">

      {/* ================= WATER MODEL UNAVAILABLE ================= */}

      {unsupported && (
        <>
          <div className="result-top caution">
            <Info />

            <div>
              <span>MODEL STATUS</span>
              <h3>Water-quality model unavailable</h3>
            </div>
          </div>

          <p>
            {String(
              manual.message ||
                "The water-quality model is currently unavailable."
            )}
          </p>
        </>
      )}

      {/* ================= WATER QUALITY RESULT ================= */}

      {manual && manual.available === true && (
        <>
          <div className="result-top">
            <FlaskConical />

            <div>
              <span>WATER-QUALITY SCREENING</span>
              <h3>
                {String(
                  manual.prediction ||
                    "Water-quality assessment completed"
                )}
              </h3>
            </div>

            <strong>
              {Number.isFinite(
                Number(manual.bad_quality_probability)
              )
                ? Math.round(
                    Number(manual.bad_quality_probability) * 100
                  )
                : 0}
              %
              <small>estimated bad-quality probability</small>
            </strong>
          </div>

          <p>
            <b>
              {String(manual.concern_level || "UNKNOWN")}
            </b>{" "}
            concern level. This is a model estimate for the
            dataset's real <code>Quality</code> label, not a
            HAB prediction.
          </p>

          {/* MODEL CONTRIBUTORS */}

          {Array.isArray(manual.explanation) &&
            manual.explanation.length > 0 && (
              <div className="precautions">
                <b>Model-identified contributors</b>

                {manual.explanation.map((item, index) => (
                  <span key={index}>
                    <CheckCircle2 />

                    {item &&
                    typeof item === "object" ? (
                      <>
                        {String(
                          item.feature || "Unknown feature"
                        )}

                        {" · relative contribution "}

                        {String(
                          item.relative_contribution ?? "N/A"
                        )}
                      </>
                    ) : (
                      String(item)
                    )}
                  </span>
                ))}
              </div>
            )}

          {/* RECOMMENDATIONS */}

          {Array.isArray(manual.recommendations) &&
            manual.recommendations.length > 0 && (
              <div className="precautions">
                <b>
                  Recommended precautionary measures
                </b>

                {manual.recommendations.map(
                  (recommendation, index) => (
                    <span key={index}>
                      <CheckCircle2 />
                      {String(recommendation)}
                    </span>
                  )
                )}
              </div>
            )}

          {/* HAB LIMITATION */}

          {manual.hab_limitation && (
            <p className="small-note">
              {String(manual.hab_limitation)}
            </p>
          )}

          {/* MODEL DISCLAIMER */}

          {manual.disclaimer && (
            <p className="small-note">
              {String(manual.disclaimer)}
            </p>
          )}
        </>
      )}

      {/* ================= IMAGE RESULT ================= */}

      {image && image.available === true && (
        <>
          <div className="result-top">
            <Leaf />

            <div>
              <span>IMAGE SCREENING RESULT</span>

              <h3>
                {String(
                  image.visual_assessment ||
                    "Visual assessment completed"
                )}
              </h3>
            </div>

            <strong>
              {Number.isFinite(Number(image.confidence))
                ? Math.round(
                    Number(image.confidence) * 100
                  )
                : 0}
              %
              <small>confidence</small>
            </strong>
          </div>

          <p>
            {String(
              image.explanation ||
                "The image was analyzed by the visual screening model."
            )}
          </p>

          {/* IMAGE PREDICTION */}

          {image.prediction && (
            <div className="precautions">
              <b>Detected image class</b>

              <span>
                <CheckCircle2 />
                {String(image.prediction)}
              </span>
            </div>
          )}

          {/* IMAGE RECOMMENDATIONS */}

          {Array.isArray(image.recommendations) &&
            image.recommendations.length > 0 && (
              <div className="precautions">
                <b>Recommended actions</b>

                {image.recommendations.map(
                  (recommendation, index) => (
                    <span key={index}>
                      <CheckCircle2 />
                      {String(recommendation)}
                    </span>
                  )
                )}
              </div>
            )}
        </>
      )}

      {/* ================= IMAGE MODEL UNAVAILABLE ================= */}

      {image &&
        image.available === false &&
        mode !== "manual" && (
          <>
            <div className="result-top caution">
              <Info />

              <div>
                <span>MODEL STATUS</span>
                <h3>Image model unavailable</h3>
              </div>
            </div>

            <p>
              {String(
                image.message ||
                  "The image model is currently unavailable."
              )}
            </p>

            {Array.isArray(image.dataset_classes) && (
              <div className="precautions">
                <b>Available image classes</b>

                {image.dataset_classes.map(
                  (item, index) => (
                    <span key={index}>
                      <CheckCircle2 />
                      {String(item)}
                    </span>
                  )
                )}
              </div>
            )}
          </>
        )}

      {/* ================= BOTH MODE MESSAGE ================= */}

      {mode === "both" && result?.message && (
        <p className="small-note">
          {String(result.message)}
        </p>
      )}
    </div>
  );
}

/* =========================================================
   MAIN APP
   ========================================================= */

function App() {
  const [mode, setMode] = useState("manual");

  const [values, setValues] = useState({});

  const [file, setFile] = useState(null);

  const [result, setResult] = useState(null);

  const [error, setError] = useState("");

  const [loading, setLoading] = useState(false);

  const input = useRef(null);

  const needsData = fields.every(
    ([key]) =>
      values[key] !== "" &&
      values[key] !== undefined &&
      values[key] !== null
  );

  const ready =
    mode === "image"
      ? Boolean(file)
      : mode === "both"
      ? Boolean(file && needsData)
      : needsData;

  /* =========================================================
     IMAGE SELECTION
     ========================================================= */

  const choose = (selectedFile) => {
    if (!selectedFile) return;

    if (
      !["image/jpeg", "image/png"].includes(
        selectedFile.type
      )
    ) {
      setError(
        "Please choose a PNG, JPG, or JPEG image."
      );
      return;
    }

    if (selectedFile.size > 8 * 1024 * 1024) {
      setError(
        "Image must be 8 MB or smaller."
      );
      return;
    }

    setError("");
    setFile(selectedFile);
  };

  /* =========================================================
     SUBMIT
     ========================================================= */

  const submit = async (e) => {
    e.preventDefault();

    setError("");
    setResult(null);
    setLoading(true);

    try {
      let response;

      /* ================= MANUAL ================= */

      if (mode === "manual") {
        response = await fetch(
          `${API}/predict/manual`,
          {
            method: "POST",

            headers: {
              "Content-Type": "application/json",
            },

            body: JSON.stringify(values),
          }
        );
      }

      /* ================= IMAGE / BOTH ================= */

      else {
        const formData = new FormData();

        formData.append("image", file);

        if (mode === "both") {
          formData.append(
            "environmental_data",
            JSON.stringify(values)
          );
        }

        const endpoint =
          mode === "both"
            ? "/predict/combined"
            : "/predict/image";

        response = await fetch(
          `${API}${endpoint}`,
          {
            method: "POST",
            body: formData,
          }
        );
      }

      /* ================= READ RESPONSE ================= */

      let data = null;

      const contentType =
        response.headers.get("content-type") || "";

      if (contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();

        throw new Error(
          text ||
            `Server returned HTTP ${response.status}`
        );
      }

      /* ================= SERVER ERROR ================= */

      if (!response.ok) {
        throw new Error(
          data?.message ||
            data?.error ||
            `Analysis failed with HTTP ${response.status}.`
        );
      }

      /* ================= SUCCESS ================= */

      setResult(data);
    } catch (err) {
      console.error("Assessment error:", err);

      if (
        err instanceof TypeError &&
        err.message.toLowerCase().includes("fetch")
      ) {
        setError(
          "Cannot connect to the Flask backend. Make sure the backend is running on http://localhost:5000."
        );
      } else {
        setError(
          err?.message ||
            "The request could not be completed. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     APP UI
     ========================================================= */

  return (
    <main>

      {/* ================= NAVIGATION ================= */}

      <nav>
        <a
          className="brand"
          href="#top"
        >
          <span>
            <Waves size={22} />
          </span>

          Bloom
          <span>Watch</span>
        </a>

        <div className="navlinks">
          <a href="#assess">
            Assessment
          </a>

          <a href="#method">
            Method
          </a>

          <a href="#limitations">
            Limitations
          </a>
        </div>

        <a
          className="navcta"
          href="#assess"
        >
          Start assessment
          <ChevronRight size={16} />
        </a>
      </nav>

      {/* ================= HERO ================= */}

      <section
        className="hero"
        id="top"
      >
        <div className="hero-copy">

          <div className="eyebrow">
            <Leaf size={15} />
            AI ENVIRONMENTAL DECISION SUPPORT
          </div>

          <h1>
            See the water
            <br />
            <em>with clearer evidence.</em>
          </h1>

          <p>
            BloomWatch combines real water-quality
            classification with transparent visual
            algae screening.
          </p>

          <a
            className="primary"
            href="#assess"
          >
            Assess observations
            <ChevronRight size={18} />
          </a>

          <div className="hero-notes">
            <span>
              <CheckCircle2 />
              Dataset-led
            </span>

            <span>
              <CheckCircle2 />
              No fabricated certainty
            </span>
          </div>
        </div>

        <div className="hero-orb">

          <div className="orb-label">
            CURRENT PROJECT SCOPE
          </div>

          <Waves />

          <strong>
            Water quality + visuals
          </strong>

          <p>
            HAB probability remains unavailable
            without verified historical HAB
            observations.
          </p>

          <div className="orb-chip">
            <Info size={16} />
            Honest by design
          </div>
        </div>
      </section>

      {/* ================= FACTS ================= */}

      <section className="facts">

        <div>
          <CloudSun />

          <b>7</b>

          <span>
            Water-quality features
          </span>
        </div>

        <div>
          <ImagePlus />

          <b>1,045</b>

          <span>
            Labelled screening images
          </span>
        </div>

        <div>
          <AlertTriangle />

          <b>0</b>

          <span>
            Validated HAB label columns
          </span>
        </div>

      </section>

      {/* ================= ASSESSMENT ================= */}

      <section
        className="assessment"
        id="assess"
      >

        <div className="section-intro">

          <div className="eyebrow aqua">
            ASSESSMENT STUDIO
          </div>

          <h2>
            Choose your evidence.
          </h2>

          <p>
            Water data produces a real Quality-label
            estimate. Image and water results remain
            independent rather than creating an invented
            combined HAB score.
          </p>

        </div>

        <div className="studio">

          {/* ================= MODE TABS ================= */}

          <div className="mode-tabs">

            {[
              [
                "manual",
                FlaskConical,
                "Water data",
              ],

              [
                "image",
                ImagePlus,
                "Image",
              ],

              [
                "both",
                Activity,
                "Both",
              ],
            ].map(
              ([id, Icon, label]) => (
                <button
                  type="button"
                  key={id}
                  onClick={() => {
                    setMode(id);
                    setResult(null);
                    setError("");
                  }}
                  className={
                    mode === id
                      ? "active"
                      : ""
                  }
                >
                  <Icon size={18} />
                  {label}
                </button>
              )
            )}

          </div>

          {/* ================= FORM ================= */}

          <form onSubmit={submit}>

            {/* WATER DATA */}

            {mode !== "image" && (
              <div className="field-grid">

                {fields.map(
                  ([key, label]) => (
                    <label key={key}>

                      {label}

                      <span>
                        Source unit
                      </span>

                      <input
                        required
                        type="number"
                        step="any"
                        inputMode="decimal"
                        value={
                          values[key] ?? ""
                        }
                        onChange={(e) =>
                          setValues({
                            ...values,
                            [key]:
                              e.target.value,
                          })
                        }
                        placeholder="Enter value"
                      />

                    </label>
                  )
                )}

              </div>
            )}

            {/* IMAGE UPLOAD */}

            {mode !== "manual" && (
              <div
                className={
                  "dropzone " +
                  (file
                    ? "selected"
                    : "")
                }
                onDragOver={(e) =>
                  e.preventDefault()
                }
                onDrop={(e) => {
                  e.preventDefault();

                  choose(
                    e.dataTransfer.files[0]
                  );
                }}
                onClick={() =>
                  input.current?.click()
                }
              >

                <input
                  ref={input}
                  onChange={(e) =>
                    choose(
                      e.target.files[0]
                    )
                  }
                  type="file"
                  accept="image/png,image/jpeg"
                  hidden
                />

                <Upload size={25} />

                {file ? (
                  <>
                    <b>
                      {file.name}
                    </b>

                    <small>
                      {(
                        file.size /
                        1024 /
                        1024
                      ).toFixed(2)}{" "}
                      MB · ready to
                      analyze
                    </small>

                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                    >
                      <X size={16} />
                      Remove
                    </button>
                  </>
                ) : (
                  <>
                    <b>
                      Drop a water image
                      here
                    </b>

                    <small>
                      PNG, JPG or JPEG ·
                      maximum 8 MB
                    </small>

                    <u>
                      Browse files
                    </u>
                  </>
                )}

              </div>
            )}

            {/* ANALYZE BUTTON */}

            <button
              className="analyze"
              type="submit"
              disabled={!ready || loading}
            >

              {loading ? (
                <>
                  <LoaderCircle className="spin" />
                  Analyzing…
                </>
              ) : (
                <>
                  {mode === "image"
                    ? "Analyze image"
                    : mode === "both"
                    ? "Generate assessment"
                    : "Analyze water data"}

                  <ChevronRight size={18} />
                </>
              )}

            </button>

          </form>

          {/* ================= ERROR ================= */}

          {error && (
            <div className="message error">

              <ShieldAlert />

              <span>
                {String(error)}
              </span>

            </div>
          )}

          {/* ================= RESULT ================= */}

          {result && (
            <Result
              result={result}
              mode={mode}
            />
          )}

        </div>
      </section>

      {/* ================= METHOD ================= */}

      <section
        className="method"
        id="method"
      >

        <div>

          <div className="eyebrow aqua">
            REAL DATA, CLEAR BOUNDARIES
          </div>

          <h2>
            What the project can say.
          </h2>

          <p>
            The image workflow retains the supplied
            paddy dataset's actual three classes:
            algae, early-stage algae, and not algae.
            Its result is a visual screen—not laboratory
            HAB confirmation.
          </p>

        </div>

        <div className="method-cards">

          <article>
            <ImagePlus />

            <h3>
              Image model
            </h3>

            <p>
              MobileNetV2 transfer learning, with real
              classes retained and evaluation saved
              after training.
            </p>
          </article>

          <article>
            <FlaskConical />

            <h3>
              Water-quality model
            </h3>

            <p>
              Five classifiers are trained against the
              supplied real <code>Quality</code> label,
              never treated as a HAB label.
            </p>
          </article>

        </div>

      </section>

      {/* ================= LIMITATIONS ================= */}

      <section
        className="limit"
        id="limitations"
      >

        <Info />

        <div>

          <h2>
            Water-quality estimate,
            not a HAB forecast
          </h2>

          <p>
            The supplied datasets do not link
            environmental conditions to future HAB
            outcomes. BloomWatch does not claim a
            48–72 hour warning window or display a HAB
            probability.
          </p>

        </div>

      </section>

      {/* ================= FOOTER ================= */}

      <footer>
        BloomWatch · Academic AI decision support ·
        Results do not replace laboratory testing or
        official environmental assessment.
      </footer>

    </main>
  );
}

/* =========================================================
   REACT ROOT
   ========================================================= */

const rootElement =
  document.getElementById("root");

if (!rootElement) {
  throw new Error(
    "Root element not found. Check index.html."
  );
}

createRoot(rootElement).render(
  <App />
);