class Logger {
	// config log levels
	constructor(LOG_LEVEL = debug) {
		const levels = {
			error: 0,
			info: 1,
			warn: 2,
			debug: 3,
		};
		// defaults log level to debug for invalid log levels
		this.LOG_LEVEL = levels[LOG_LEVEL] ?? levels["debug"];
	}
	#format(level, message, ...meta) {
		let metaData = meta.length ? `${JSON.stringify(meta)}` : "";

		// different color coding for error and other levels
		if (level === "error") {
			if (!(message instanceof Error)) {
				message = new Error("Undefined error");
			}
			process.stdout.write(logColor(level) + `[${level}] ${message.stack}${metaData ? `\n${metaData}` : ""}\x1b[0m\n`);
		} else {
			const coloredLevel = logColor(level) + `[${level}]` + "\x1b[0m";
			process.stdout.write(
				`${coloredLevel} ${typeof message === "string" ? message : JSON.stringify(message)}${metaData ? `\n${metaData}` : ""}\n`,
			);
		}
	}

	#log(level, message, ...meta) {
		this.#format(level, message, ...meta);
	}

	error(err, ...args) {
		this.#log("error", err, ...args);
	}

	info(message, ...args) {
		if (this.LOG_LEVEL >= 1) this.#log("info", message, ...args);
	}

	warn(message, ...args) {
		if (this.LOG_LEVEL >= 2) this.#log("warn", message, ...args);
	}

	debug(message, ...args) {
		if (this.LOG_LEVEL >= 3) this.#log("debug", message, ...args);
	}
}

// helper function for colors
const logColor = (level) => {
	const colors = {
		error: "\x1b[91m", // red
		warn: "\x1b[93m", // yellow
		info: "\x1b[96m", // cyan
		debug: "\x1b[95m", // magenta
	};
	return colors[level] || "\x1b[37m"; // default white
};

export const logger = new Logger(process.env.LOG_LEVEL);
