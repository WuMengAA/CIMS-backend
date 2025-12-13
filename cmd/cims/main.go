package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"path/filepath"

	"github.com/MINIOpenSource/CIMS-backend/internal/api/grpc"
	v1 "github.com/MINIOpenSource/CIMS-backend/internal/api/http/v1"
	"github.com/MINIOpenSource/CIMS-backend/internal/data"
	"github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Service"
	"github.com/gin-gonic/gin"
	"github.com/kardianos/service"
	"github.com/spf13/cobra"
	googlegrpc "google.golang.org/grpc"
)

var (
	dbPath  string
	port    int
	grpcPort int
)

type program struct{}

func (p *program) Start(s service.Service) error {
	go p.run()
	return nil
}

func (p *program) run() {
	if err := data.InitDB(dbPath); err != nil {
		log.Fatalf("Failed to init DB: %v", err)
	}

	// Start gRPC
	go func() {
		lis, err := net.Listen("tcp", fmt.Sprintf(":%d", grpcPort))
		if err != nil {
			log.Fatalf("failed to listen: %v", err)
		}
		s := googlegrpc.NewServer()
		Service.RegisterClientRegisterServer(s, grpc.NewClientRegisterServer())
		Service.RegisterClientCommandDeliverServer(s, grpc.NewClientCommandDeliverServer())

		log.Printf("gRPC server listening at %v", lis.Addr())
		if err := s.Serve(lis); err != nil {
			log.Fatalf("failed to serve: %v", err)
		}
	}()

	// Start HTTP
	r := gin.Default()
	v1Group := r.Group("/api/v1")
	clientHandler := v1.NewClientHandler()
	clientHandler.RegisterRoutes(v1Group)

	mgmtHandler := v1.NewMgmtHandler()
	mgmtHandler.RegisterRoutes(r.Group("/"))

	log.Printf("HTTP server listening at :%d", port)
	if err := r.Run(fmt.Sprintf(":%d", port)); err != nil {
		log.Fatalf("failed to run server: %v", err)
	}
}

func (p *program) Stop(s service.Service) error {
	return nil
}

func main() {
	var rootCmd = &cobra.Command{
		Use:   "cims",
		Short: "ClassIsland Management Server",
	}

	rootCmd.PersistentFlags().StringVar(&dbPath, "db", "cims.db", "Path to SQLite database")
	rootCmd.PersistentFlags().IntVar(&port, "port", 50050, "HTTP Port")
	rootCmd.PersistentFlags().IntVar(&grpcPort, "grpc-port", 50051, "gRPC Port")

	absDbPath, _ := filepath.Abs(dbPath)
	svcConfig := &service.Config{
		Name:        "cims",
		DisplayName: "ClassIsland Management Server",
		Description: "Backend service for ClassIsland.",
		Arguments:   []string{"start", "--db", absDbPath},
	}

	prg := &program{}
	s, err := service.New(prg, svcConfig)
	if err != nil {
		log.Fatal(err)
	}

	var startCmd = &cobra.Command{
		Use:   "start",
		Short: "Start the server",
		Run: func(cmd *cobra.Command, args []string) {
			if err := s.Run(); err != nil {
				log.Fatal(err)
			}
		},
	}

	var serviceCmd = &cobra.Command{
		Use:   "service",
		Short: "Manage system service",
	}

	serviceCmd.AddCommand(&cobra.Command{
		Use:   "install",
		Short: "Install as system service",
		Run: func(cmd *cobra.Command, args []string) {
			absPath, _ := filepath.Abs(dbPath)
			svcConfig.Arguments = []string{"start", "--db", absPath}
			s, _ := service.New(prg, svcConfig)
			if err := s.Install(); err != nil {
				log.Fatalf("Failed to install: %v", err)
			}
			fmt.Println("Service installed successfully.")
		},
	})

	serviceCmd.AddCommand(&cobra.Command{
		Use:   "uninstall",
		Short: "Uninstall system service",
		Run: func(cmd *cobra.Command, args []string) {
			if err := s.Uninstall(); err != nil {
				log.Fatalf("Failed to uninstall: %v", err)
			}
			fmt.Println("Service uninstalled successfully.")
		},
	})

	serviceCmd.AddCommand(&cobra.Command{
		Use:   "run",
		Short: "Start the system service",
		Run: func(cmd *cobra.Command, args []string) {
			if err := s.Start(); err != nil {
				log.Fatalf("Failed to start service: %v", err)
			}
			fmt.Println("Service started.")
		},
	})

	serviceCmd.AddCommand(&cobra.Command{
		Use:   "stop",
		Short: "Stop the system service",
		Run: func(cmd *cobra.Command, args []string) {
			if err := s.Stop(); err != nil {
				log.Fatalf("Failed to stop service: %v", err)
			}
			fmt.Println("Service stopped.")
		},
	})

	var initCmd = &cobra.Command{
		Use:   "init",
		Short: "Initialize configuration",
		Run: func(cmd *cobra.Command, args []string) {
			if err := data.InitDB(dbPath); err != nil {
				log.Fatalf("Failed to init DB: %v", err)
			}
			fmt.Println("Database initialized.")
		},
	}

	rootCmd.AddCommand(startCmd)
	rootCmd.AddCommand(serviceCmd)
	rootCmd.AddCommand(initCmd)

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
